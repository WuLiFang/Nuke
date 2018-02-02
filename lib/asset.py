# -*- coding: UTF-8 -*-
"""Deal with assets and files in nuke."""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import multiprocessing.dummy as multiprocessing
import os
import re
import time
from collections import namedtuple
from functools import wraps

import nuke

from edit import clear_selection
from node import Last
from wlf.decorators import run_with_clock
from wlf.env import has_gui
from wlf.files import Path, copy
from wlf.path import get_encoded as e
from wlf.path import get_unicode as u
from wlf.path import expand_frame, get_footage_name, is_ascii
from nuketools import utf8

LOGGER = logging.getLogger('com.wlf.asset')
TEMPLATES_DIR = os.path.abspath(os.path.join(__file__, '../templates'))

CACHED_ASSET = set()

# Asset type
A_SEQUENCE = 1 << 0
A_SINGLEFILE = 1 << 1

CachedDropframes = namedtuple('CachedDropframes',
                              ['dropframes', 'timestamp'])


class Asset(object):
    """Asset for nuke node.  """

    update_interval = 10

    def __new__(cls, filename):
        # Try find cached asset.
        for i in CACHED_ASSET:
            assert isinstance(i, Asset)
            if u(i.filename) == u(cls.filename_factory(filename)):
                return i
        ret = super(Asset, cls).__new__(cls, filename)
        CACHED_ASSET.add(ret)
        return ret

    def __init__(self, filename):
        filename = self.filename_factory(filename)
        self.filename = filename
        self.is_showed = False
        self._dropframes = None

        self.type = (A_SINGLEFILE
                     if filename.with_frame(1) == filename.with_frame(2)
                     else A_SEQUENCE)

    def __str__(self):
        return e('Asset: {}'.format(self.filename))

    @classmethod
    def filename_factory(cls, obj):
        """get filename from a object as filename.

        Args:
            obj (str or unicode or nuke.Node): Object contain filename.

        Returns:
            wlf.path.Path: filename path.
        """

        filename = obj
        if isinstance(obj, nuke.Node):
            filename = nuke.filename(obj)

        path = Path(filename)
        return path

    def dropframes(self, frame_list=None):
        # type: (...) -> nuke.FrameRanges
        """Get drop frames compare with frame_list.

        Args:
            frame_list (Iterable[int] or nuke.Node or nuke.FrameRanges, optional): Defaults to None.
                check file exsits with these frames,
                None mean Root frame range.

        Returns:
            nuke.FrameRanges: dropframe ranges.
        """

        if frame_list is None:
            frame_list = nuke.Root().frameRange()
        # suport nuke.Node as input
        elif isinstance(frame_list, nuke.Node):
            frame_list = frame_list.frameRange()
        # suport nuke.FrameRanges as input
        elif isinstance(frame_list, nuke.FrameRanges):
            frame_list = frame_list.toFrameList()

        # Try used caced result.
        if (isinstance(self._dropframes, CachedDropframes)
                and time.time() - self._dropframes.timestamp < self.update_interval):
            cached = self._dropframes.dropframes
            assert isinstance(cached, nuke.FrameRanges)
            ret = nuke.FrameRanges([i for i in cached.toFrameList()
                                    if i in frame_list])
            ret.compact()
            # Skip cache phase.
            return ret

        elif self.type & A_SEQUENCE:
            ret = nuke.FrameRanges()
            checked = set()

            def _check(frame):
                try:
                    path = Path(Path(self.filename).with_frame(frame))
                    if path in checked:
                        return
                    if not path.is_file():
                        ret.add([frame])
                    checked.add(path)
                except OSError as ex:
                    LOGGER.error(os.strerror(ex.errno), exc_info=True)

            pool = multiprocessing.Pool()
            pool.map(_check, frame_list)
            pool.close()
            pool.join()
            ret.compact()
        elif self.type & A_SINGLEFILE:
            ret = nuke.FrameRanges(
                frame_list if not self.filename.exists() else [])
        else:
            raise NotImplementedError

        # Cache result.
        if not set(nuke.Root().frameRange()).difference(frame_list):
            self._dropframes = CachedDropframes(ret, time.time())
        return ret


class DropFrames(object):
    """Check drop frames and record on the node."""

    _showed_files = set()
    _file_dropframe = {}

    @classmethod
    def get(cls, filename, default=None):
        """Get dropframes for @filename"""
        return cls._file_dropframe.get(filename, default)

    @classmethod
    def check(cls, show_ok=False):
        """Check dropframe then show them if any.  """

        cls._file_dropframe.clear()
        cls.update()
        cls.show(show_all=True, show_ok=show_ok)

    @classmethod
    @run_with_clock('检查缺帧')
    def update(cls, nodes=None):
        """update self."""
        if isinstance(nodes, nuke.Node):
            nodes = [nodes]
        nodes = nodes or nuke.allNodes('Read')
        if not nodes:
            return

        footages = get_footages(nodes)

        def _check(filename):
            try:
                framerange = footages[filename]
                framerange.compact()
                dropframes = get_dropframe(filename, framerange.toFrameList())
                if str(dropframes):
                    cls._file_dropframe[filename] = dropframes
                elif cls._file_dropframe.has_key(filename):
                    del cls._file_dropframe[filename]
            except:
                LOGGER.error(
                    'Unexpected exception during check dropframes.', exc_info=True)
                raise
        pool = multiprocessing.Pool()
        pool.map(_check, footages)
        pool.close()
        pool.join()

    @classmethod
    def show(cls, show_all=False, show_ok=False):
        """Show all dropframes to user."""
        message = ''
        for filename, dropframes in cls._file_dropframe.items():
            if not show_all\
                    and filename in cls._showed_files:
                continue
            if dropframes:
                message += '<tr><td><span style=\"color:red\">{}</span>'\
                    '</td><td>{}</td></tr>'.format(dropframes, filename)
                cls._showed_files.add(filename)

        if message:
            message = '<style>td{padding:8px;}</style>'\
                '<table>'\
                '<tr><th>缺帧</th><th>素材</th></tr>'\
                + message +\
                '</table>'
            nuke.message(message)
        elif show_ok:
            nuke.message('没有发现缺帧素材')


def warn_dropframes(show_all=False, show_ok=False):
    @run_with_clock('检查缺帧')
    def _check():
        nodes = nuke.allNodes('Read')
        ret = {}

        def _check_node(node):
            asset = Asset(node)
            dropframes = asset.dropframes(node)
            if dropframes:
                key = u(asset.filename.as_posix())
                ret.setdefault(key, nuke.FrameRanges())
                ret[key].add(dropframes)
        pool = multiprocessing.Pool()
        pool.map(_check_node, nodes)
        pool.close()
        pool.join()

        return ret

    # env = Environment(
    #     loader=PackageLoader(__name__),
    # )

    # template = env.get_template('csheet.html')
    ret = _check()
    # return template.render(**updated_config(config))
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template('dropframes.html')
    msg = template.render(data=ret.items())
    nuke.message(utf8(msg))
    return ret


def warn_mtime(show_dialog=False, show_ok=False):
    """Show footage that mtime newer than script mtime. """

    LOGGER.debug('Check warn_mtime')
    msg = ''
    newer_footages = {}

    @run_with_clock('检查素材修改日期')
    def _get_mtime_info():
        for n in nuke.allNodes('Read', nuke.Root()):
            try:
                mtime = time.strptime(n.metadata(
                    'input/mtime'), '%Y-%m-%d %H:%M:%S')
            except TypeError:
                continue
            if mtime > Last.mtime:
                ftime = time.strftime('%m-%d %H:%M:%S', mtime)
                newer_footages[nuke.filename(n)] = ftime
                msg = '{}: [new footage]{}'.format(n.name(), ftime)
                if msg not in Last.showed_warning:
                    nuke.warning(msg)
                    Last.showed_warning.append(msg)

    _get_mtime_info()

    if show_dialog and (newer_footages or show_ok):
        msg = '<style>td {padding:8px;}</style>'
        msg += u'<b>{}</b>'.format((os.path.basename(Last.name)))
        msg += u'<div>上次修改: {}</div><br><br>'.format(
            time.strftime('%y-%m-%d %H:%M:%S', Last.mtime))
        if newer_footages:
            msg += u'发现以下素材变更:<br>'
            msg += '<tabel>'
            msg += '<tr><th>修改日期</th><th>素材</th></tr>'
            msg += '\n'.join(['<tr><td>{}</td><td>{}</td></tr>'.format(newer_footages[i], i)
                              for i in newer_footages])
            msg += '</tabel>'
        elif show_ok:
            msg += u'没有发现更新的素材'
        nuke.message(msg)


def get_footages(nodes=None):
    """Footage used for @nodes.  """

    nodes = nodes or nuke.allNodes('Read')
    nodes = list(n for n in nodes if 'disable' in n.knobs()
                 and not n['disable'].value())

    ret = {}
    for n in nodes:
        if n.Class() != 'Read':
            continue
        filename = nuke.filename(n)
        ret.setdefault(filename, nuke.FrameRanges())
        # `nuke.Node.frameRange` may wrong when using `frame` knob.
        framerange = nuke.FrameRange(
            '{:.0f}-{:.0f}'.format(n['first'].value(), n['last'].value()))
        ret[filename].add(framerange)
    return ret


def get_dropframe(filename, framerange):
    """Return dropframes for @filename in @framerange. -> nuke.FrameRanges """

    from wlf.notify import Progress, CancelledError

    assert isinstance(framerange, (list, nuke.FrameRange))
    filename = u(filename)
    dir_path = os.path.dirname(filename)

    task = Progress(u'验证文件', total=len(framerange))
    ret = nuke.FrameRanges()
    if not os.path.isdir(e(dir_path)) or \
        (expand_frame(filename, 1) == filename
         and not os.path.isfile(e(filename))):
        ret.add(framerange)
        return ret

    files = os.listdir(e(dir_path))
    basename = os.path.basename(filename)
    for f in framerange:
        frame_file = expand_frame(basename, f)
        task.step(frame_file)
        if e(frame_file) not in files:
            ret.add([f])
    ret.compact()
    return ret


def sent_to_dir(dir_):
    """Send current working file to dir."""

    copy(nuke.value('root.name'), dir_, threading=True)


def dropdata_handler(mime_type, data, from_dir=False):
    """Handling dropdata."""

    from wlf.notify import Progress, CancelledError

    LOGGER.debug('Handling dropdata: %s %s', mime_type, data)
    if mime_type != 'text/plain':
        return
    data = u(data)

    def _isdir():
        if os.path.isdir(e(data)):
            _dirname = data.replace('\\', '/')
            filenames = nuke.getFileNameList(e(_dirname, 'UTF-8'))
            task = Progress(data, total=len(filenames))
            for filename in filenames:
                try:
                    task.step(filename)
                except CancelledError:
                    return True
                dropdata_handler(
                    mime_type, '{}/{}'.format(_dirname, filename), from_dir=True)
            return True

    def _ignore():
        ignore_pat = (r'thumbs\.db$', r'.*\.lock$', r'.* - 副本\b')
        filename = os.path.basename(data)
        for pat in ignore_pat:
            if re.match(u(pat), u(filename), flags=re.I | re.U):
                return True
        if data.endswith('.mov') and not is_ascii(data):
            nuke.createNode(
                'StickyNote', 'autolabel {{\'<div align="center">\'+autolabel()+\'</div>\'}} '
                'label {{{}\n\n<span style="color:red;text-align:center;font-weight:bold">'
                'mov格式使用非英文路径将可能导致崩溃</span>}}'.format(data), inpanel=False)
            return True

    def _file_protocol():
        match = re.match(r'file://+([^/].*)', data)
        if match:
            _data = match.group(1)
            return dropdata_handler(mime_type, _data, from_dir=True)

    def _fbx():
        if data.endswith('.fbx'):
            n = nuke.createNode(
                'Camera2',
                'read_from_file True '
                'frame_rate 25 '
                'suppress_dialog True '
                'label {'
                '导入的摄像机：\n'
                '[basename [value file]]\n}')
            n.setName('Camera_3DEnv_1')
            n['file'].fromUserText(data)
            if nuke.expression('{}.animated'.format(n.name())):
                n['read_from_file'].setValue(False)

            n = nuke.createNode('ReadGeo2')
            n['file'].fromUserText(data)
            n['all_objects'].setValue(True)
            return True

    def _vf():
        if data.endswith('.vf'):
            nuke.createNode(
                'Vectorfield',
                'vfield_file "{data}" '
                'file_type vf '
                'label {{[value this.vfield_file]}}'.format(data=data.replace('\\', '/')))
            return True

    def _nk():
        if data.endswith('.nk'):
            nuke.scriptReadFile(data)
            return True

    def _video():
        if data.endswith(('.mov', '.mp4', '.avi')):

            n = nuke.createNode('Read', 'file "{}"'.format(data))
            if n.hasError():
                n['disable'].setValue(True)
            return True

    def _from_dir():
        if from_dir:
            n = nuke.createNode(
                'Read', 'file "{}"'.format(data), inpanel=False)
            DropFrames.update(n)
            if n.hasError():
                n['disable'].setValue(True)
            return True

    clear_selection()
    for func in (_isdir, _ignore, _file_protocol, _video, _vf, _fbx, _from_dir, _nk):
        if func():
            return True


def fix_error_read():
    """Try fix all read nodes that has error."""

    def _get_name(filename):
        return os.path.basename(get_footage_name(filename))

    filename_dict = {_get_name(nuke.filename(n)): nuke.filename(n)
                     for n in nuke.allNodes('Read') if not n.hasError()}
    for n in nuke.allNodes('Read'):
        if not n.hasError() or n['disable'].value():
            continue
        fix_result = None
        filename = nuke.filename(n)
        name = os.path.basename(nuke.filename(n))
        new_path = filename_dict.get(_get_name(name))
        if os.path.basename(filename).lower() == 'thumbs.db':
            fix_result = True
        elif new_path:
            filename_knob = n['file'] if not n['proxy'].value() \
                or nuke.value('root.proxy') == 'false' else n['proxy']
            filename_knob.setValue(new_path)
        else:
            fix_result = dropdata_handler('text/plain', filename)
        if fix_result:
            nuke.delete(n)


def check_localization_support(func):
    """Decorator.  """

    @wraps(func)
    def _func(*args, **kwargs):
        if nuke.env['NukeVersionMajor'] < 10:
            print('Localization update only support Nuke10.0 or above.')
            return
        func(*args, **kwargs)

    return _func


if has_gui():
    from Qt.QtCore import QTimer

    class Localization(object):
        """Nuke localization utility.  """

        timer = QTimer()

        @classmethod
        def start_upate(cls, interval=1800):
            """Start update thread"""

            cls.timer.setInterval(interval * 1000)
            cls.timer.start()

        @staticmethod
        @check_localization_support
        def update():
            """Update localized files"""

            LOGGER.info(u'清理素材缓存')
            import nuke.localization as localization
            localization.clearUnusedFiles()
            localization.pauseLocalization()
            localization.forceUpdateAll()
            localization.setAlwaysUseSourceFiles(True)

    Localization.timer.timeout.connect(Localization.update)
