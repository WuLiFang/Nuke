# -*- coding: UTF-8 -*-
"""Deal with assets and files in nuke."""

from __future__ import absolute_import, print_function, unicode_literals

import io
import logging
import multiprocessing.dummy as multiprocessing
import os
import re
import time
import webbrowser
from collections import namedtuple
from functools import wraps
from tempfile import mkstemp

import nuke
from jinja2 import Environment, PackageLoader

from edit import clear_selection
from node import Last
from nuketools import utf8
from wlf.decorators import run_with_clock
from wlf.env import has_gui
from wlf.files import Path, copy, PurePath
from wlf.path import get_encoded as e
from wlf.path import get_unicode as u
from wlf.path import expand_frame, get_footage_name, is_ascii

LOGGER = logging.getLogger('com.wlf.asset')
TEMPLATES_DIR = os.path.abspath(os.path.join(__file__, '../templates'))

CACHED_ASSET = set()

# Asset type
A_SEQUENCE = 1 << 0
A_SINGLEFILE = 1 << 1

CachedMissingFrames = namedtuple('CachedMissingFrames',
                                 ['frame_ranges', 'timestamp'])


class Assets(list):
    """Multiple Asset. Get assets from a obj.

    Args:
        obj (Assets supported types): object may contain multiple assets.
        is_strict (bool) : Defaults to False, strict mode switch.

    Raises:
        ValueError: when `is_strict` is True and can not get assets from `obj`.

    Returns:
        list[Asset]: List of asset in `obj`, or all_assets as default.
    """

    def __init__(self, obj, is_strict=False):
        if isinstance(obj, Assets):
            list_ = obj
        else:
            try:
                list_ = [Asset(obj)]
            except TypeError:
                try:
                    list_ = list(Asset(i) for i in obj)
                except TypeError:
                    if is_strict:
                        raise ValueError('not supported type: {}', type(obj))
                    list_ = self.all()
        super(Assets, self).__init__(list_)

    @classmethod
    def all(cls):
        """Get all assets current using.

        Returns:
            Assets: current assets.
        """

        return cls(nuke.allNodes('Read'))

    @run_with_clock('检查缺帧')
    def missing_frames_dict(self):
        """Get dropframes from assets.

        Decorators:
            run_with_clock

        Returns:
            DropFramesDict: Dict of (asset, dropframes) pair.
        """

        ret = MissingFramesDict()

        def _run(asset):
            assert isinstance(asset, Asset)
            dropframes = asset.missing_frames()
            if dropframes:
                key = u(asset.filename.as_posix())
                ret.setdefault(key, nuke.FrameRanges())
                ret[key].add(dropframes)

        pool = multiprocessing.Pool()
        pool.map(_run, self)
        pool.close()
        pool.join()

        return ret


class Asset(object):
    """Asset for nuke node.  """

    update_interval = 10

    def __new__(cls, filename, frame_ranges=None):
        # Skip new from other Asset objet.
        if isinstance(filename, Asset):
            return filename
        # Try find cached asset.
        for i in CACHED_ASSET:
            assert isinstance(i, Asset)
            if u(i.filename) == u(cls.filename_factory(filename)):
                return i
        return super(Asset, cls).__new__(cls, filename)

    def __init__(self, filename, frame_ranges=None):
        # Skip init from other Asset objet.
        if isinstance(filename, Asset):
            return

        filename = self.filename_factory(filename)
        frame_ranges = self.frame_ranges_factory(frame_ranges)
        self.filename = filename
        self.frame_ranges = frame_ranges
        self._missing_frames = None

        CACHED_ASSET.add(self)

    def __str__(self):
        return e('Asset: {}'.format(self.filename))

    @classmethod
    def filename_factory(cls, obj):
        """get filename from a object.

        Args:
            obj (str or unicode or nuke.Node): Object contain filename.

        Returns:
            wlf.path.Path: filename path.
        """

        filename = obj
        if isinstance(obj, nuke.Node):
            filename = nuke.filename(obj)
        elif isinstance(obj, Asset):
            filename = obj.filename
        elif isinstance(obj, (str, unicode)):
            pass
        else:
            raise TypeError('can not use as filename: {}'.format(type(obj)))
        path = Path(u(filename))
        return path

    @classmethod
    def frame_ranges_factory(cls, obj):
        """Get frame_ranges from a object.

        Args:
            obj (nuke.Node or nuke.FrameRanges): Object contain frame_ranges.
                will use nuke.Root() when object is not acceptable.

        Returns:
            nuke.FrameRanges: frame_ranges in obj

        """

        if isinstance(obj, nuke.Node):
            return nuke.FrameRanges([obj.frameRange()])
        elif isinstance(obj, Asset):
            return obj.frame_ranges
        try:
            path = PurePath(obj)
            if path.with_frame(1) == path.with_frame(2):
                return nuke.FrameRanges([1])
        except TypeError:
            return cls.frame_ranges_factory(nuke.Root())

    def missing_frames(self, frame_ranges=None):
        """Get missing frame ranges compare to frame_list.

        Args:
            frame_list (Iterable[int] or nuke.Node or nuke.FrameRanges, optional): Defaults to None.
                check file exsits with these frames,
                None mean return whole missing frame ranges.

        Returns:
            nuke.FrameRanges: missing frame ranges.
        """

        if frame_ranges is None:
            frame_ranges = self.frame_ranges
        else:
            frame_ranges = self.frame_ranges_factory(frame_ranges)

        # Update if need.
        if (not isinstance(self._missing_frames, CachedMissingFrames)
                or time.time() - self._missing_frames.timestamp > self.update_interval):
            self._update_missing_frame()

        assert isinstance(self._missing_frames, CachedMissingFrames)
        cached = self._missing_frames.frame_ranges

        ret = nuke.FrameRanges([i for i in cached.toFrameList()
                                if i in frame_ranges.toFrameList()])
        ret.compact()
        return ret

    def _update_missing_frame(self):
        ret = nuke.FrameRanges()
        checked = set()

        def _check(frame):
            try:
                path = Path(self.filename.with_frame(frame))
                if path in checked:
                    return
                if not path.is_file():
                    ret.add([frame])
                checked.add(path)
            except OSError as ex:
                LOGGER.error(os.strerror(ex.errno), exc_info=True)

        pool = multiprocessing.Pool()
        pool.map(_check, self.frame_ranges.toFrameList())
        pool.close()
        pool.join()

        ret.compact()
        self._missing_frames = CachedMissingFrames(ret, time.time())
        return ret


class MissingFramesDict(dict):
    def __str__(self):
        rows = ['| Filename | MissingFrames |:']
        for k, v in self.items():
            rows.append('| {} | {} |'.format(k, v))
        return '\n'.join(rows)

    def as_html(self):
        env = Environment(loader=PackageLoader(__name__))
        template = env.get_template('dropframes.html')
        return template.render(data=self.items())


def warn_missing_frames(assets=None, show_ok=False):
    """Show missing frames to user
        assets (any, optional): Defaults to None.
            object contains assets, None mean all Assets.
        show_ok (bool, optional): Defaults to False.
            If show message for no missing frames.
    """

    result = Assets(assets).missing_frames_dict()
    if not result and show_ok:
        nuke.message(utf8('没有发现缺帧素材'))
    elif len(result) < 10:
        if nuke.GUI:
            nuke.message(utf8(result.as_html()))
        else:
            LOGGER.warning(result)
    else:
        # Use html to display.
        fd, name = mkstemp('.html', text=True)
        with io.open(fd, 'w') as f:
            f.write(result.as_html())
        webbrowser.open(name)


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

# Deprecated below:


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
