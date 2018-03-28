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

import callback
from edit import clear_selection
from node import Last
from nuketools import utf8
from wlf.decorators import run_with_clock
from wlf.env import has_gui
from wlf.files import Path, PurePath, copy
from wlf.path import get_encoded as e
from wlf.path import get_unicode as u
from wlf.path import is_ascii

LOGGER = logging.getLogger('com.wlf.asset')
TEMPLATES_DIR = os.path.abspath(os.path.join(__file__, '../templates'))

CACHED_ASSET = set()

# Asset type
A_SEQUENCE = 1 << 0
A_SINGLEFILE = 1 << 1

CachedMissingFrames = namedtuple('CachedMissingFrames',
                                 ['frame_ranges', 'timestamp'])


class FrameRanges(object):
    """Wrap a object for get nuke.FrameRanges.

    Args:
        obj (any): Object contains frame_ranges.
            will use nuke.Root() instead when object is not support.
    """

    def __init__(self, obj=None):
        self._wrapped = obj
        self._list = None
        self._node_filename = (nuke.filename(obj)
                               if isinstance(obj, nuke.Node) else None)

    @property
    def wrapped(self):
        obj = self._wrapped
        if isinstance(obj, nuke.FrameRanges):
            return obj

        # Get frame_list from obj
        try:
            # LOGGER.debug('get from %s', type(obj))
            if self._wrapped is None:
                raise TypeError
            elif isinstance(obj, (list, nuke.FrameRange)):
                list_ = list(obj)
            elif isinstance(obj, nuke.Root):
                first = int(obj['first_frame'].value())
                last = int(obj['last_frame'].value())
                if first > last:
                    first, last = last, first
                list_ = range(first, last+1)
            elif isinstance(obj, nuke.Node):
                is_deleted = True
                try:
                    repr(obj)
                    is_deleted = False
                except ValueError:
                    pass
                # When node deleted or filename changed,
                # use previous result.
                if (is_deleted
                        or nuke.filename(obj) != self._node_filename):
                    list_ = self._list
                    if list_ is None:
                        raise TypeError
                else:
                    first = obj.firstFrame()
                    last = obj.lastFrame()
                    if first > last:
                        first, last = last, first
                    list_ = range(first, last+1)
            elif isinstance(obj, Asset):
                list_ = obj.frame_ranges.toFrameList()
            elif isinstance(obj, FrameRanges):
                list_ = obj.wrapped.toFrameList()
            elif (isinstance(obj, (str, unicode))
                  and re.match(r'^[\d -x]*$', u(obj))):
                # Parse Nuke frameranges string:
                try:
                    list_ = nuke.FrameRanges(obj).toFrameList()
                except RuntimeError:
                    raise TypeError
            elif isinstance(obj, (str, unicode, PurePath)):
                # Reconize as single frame
                path = PurePath(obj)
                if path.with_frame(1) == path.with_frame(2):
                    list_ = [1]
                else:
                    raise TypeError
            else:
                raise TypeError

            self._list = list_
            ret = nuke.FrameRanges(list_)

            # Save result for some case.
            if isinstance(obj, (list, str, unicode, PurePath)):
                self._wrapped = ret

            self._wrapped_result = ret
            return ret
        except TypeError:
            self._wrapped = None
            return self.from_root()

    def __str__(self):
        return str(self.wrapped)

    def __add__(self, other):
        if isinstance(other, (nuke.FrameRanges, FrameRanges)):
            ret = FrameRanges(self.toFrameList() + other.toFrameList())
            ret.compact()
        else:
            raise TypeError(
                'FrameRanges.__add__ not support:{}'.format(type(other)))

        return ret

    def __getattr__(self, name):
        return getattr(self.wrapped, name)

    def __nonzero__(self):
        return bool(self.to_frame_list())

    def to_frame_list(self):
        """nuke.FrameRanges will returns None if no frame in it.
        this will return a empty list.

        Returns:
            list: Frame list in this frame ranges.
        """
        ret = self.wrapped.toFrameList()
        if ret is None:
            ret = []
        return ret

    @classmethod
    def from_root(cls):
        root = nuke.Root()
        first = root['first_frame'].value()
        last = root['last_frame'].value()
        ret = nuke.FrameRanges(first, last, 1)
        ret = FrameRanges(ret)
        return FrameRanges(nuke.Root())


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
                list_ = set(Asset(obj))
            except TypeError:
                try:
                    list_ = list(Asset(i) for i in obj)
                except TypeError:
                    if is_strict:
                        raise TypeError('Not supported type: {}', type(obj))
                    list_ = []
        super(Assets, self).__init__(set(list_))

    def __str__(self):
        return e(self.__unicode__())

    def __unicode__(self):
        return [u(i) for i in self]

    @classmethod
    def all(cls):
        """Get all assets current using.

        Returns:
            Assets: current assets.
        """

        return cls(nuke.allNodes('Read'))

    @run_with_clock('检查缺帧')
    def missing_frames_dict(self):
        """Get missing_frames from assets.

        Decorators:
            run_with_clock

        Returns:
            DropFramesDict: Dict of (asset, missing_frames) pair.
        """

        ret = MissingFramesDict()

        def _run(asset):
            assert isinstance(asset, Asset)
            try:
                missing_frames = asset.missing_frames()
                if missing_frames:
                    key = u(asset.filename.as_posix())
                    if key in ret:
                        ret[key].add(missing_frames)
                    else:
                        ret[key] = missing_frames
            except:
                import traceback
                raise RuntimeError(traceback.format_exc())

        if self:
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

        frame_ranges = filename if frame_ranges is None else frame_ranges
        filename = cls.filename_factory(filename)

        # Try find cached asset.
        for i in CACHED_ASSET:
            assert isinstance(i, Asset)
            if u(i.filename) == u(filename):
                if filename.with_frame(1) != filename.with_frame(2):
                    i.frame_ranges += FrameRanges(frame_ranges)
                return i
        return super(Asset, cls).__new__(cls)

    def __init__(self, filename, frame_ranges=None):
        # Skip init cached Asset objet.
        if self in CACHED_ASSET:
            return

        frame_ranges = filename if frame_ranges is None else frame_ranges
        filename = self.filename_factory(filename)
        self.filename = filename
        self.frame_ranges = FrameRanges(frame_ranges)
        self._missing_frames = None

        CACHED_ASSET.add(self)

    def __unicode__(self):
        return '素材: {0.filename} {0.frame_ranges}'.format(self)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

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

    def missing_frames(self, frame_ranges=None):
        """Get missing frame ranges compare to frame_list.

        Args:
            frame_list (Iterable[int] or nuke.Node or nuke.FrameRanges, optional): Defaults to None.
                check file exsits with these frames,
                None mean return whole missing frame ranges.

        Returns:
            FrameRanges: missing frame ranges.
        """

        if frame_ranges is None:
            frame_ranges = self.frame_ranges
        else:
            frame_ranges = FrameRanges(frame_ranges)

        # Update if need.
        if (not isinstance(self._missing_frames, CachedMissingFrames)
                or time.time() - self._missing_frames.timestamp > self.update_interval):
            self._update_missing_frame()

        assert isinstance(self._missing_frames, CachedMissingFrames)
        cached = self._missing_frames.frame_ranges

        ret = FrameRanges([i for i in cached.to_frame_list()
                           if i in frame_ranges.to_frame_list()])
        ret.compact()
        return ret

    def _update_missing_frame(self):
        ret = FrameRanges([])
        checked = set()
        frames = self.frame_ranges.toFrameList()

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
        pool.map(_check, frames)
        pool.close()
        pool.join()

        ret.compact()
        self._missing_frames = CachedMissingFrames(ret, time.time())
        if ret:
            msg = '{} 缺帧: {}'.format(self, ret)
            nuke.warning(utf8(msg))
        return ret


class MissingFramesDict(dict):
    def __str__(self):
        rows = ['| Filename | MissingFrames |:']
        for k in sorted(self):
            rows.append('| {} | {} |'.format(k, self[k]))
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

    if assets is None:
        assets = Assets.all()
    else:
        assets = Assets(assets)

    result = assets.missing_frames_dict()
    if not result:
        if show_ok:
            nuke.message(utf8('没有发现缺帧素材'))
    elif len(result) < 10:
        if nuke.GUI:
            nuke.message(utf8(result.as_html().replace('\n', '')))
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
        msg += '<b>{}</b>'.format((os.path.basename(Last.name)))
        msg += '<div>上次修改: {}</div><br><br>'.format(
            time.strftime('%y-%m-%d %H:%M:%S', Last.mtime))
        if newer_footages:
            msg += '发现以下素材变更:<br>'
            msg += '<tabel>'
            msg += '<tr><th>修改日期</th><th>素材</th></tr>'
            msg += '\n'.join(['<tr><td>{}</td><td>{}</td></tr>'.format(newer_footages[i], i)
                              for i in newer_footages])
            msg += '</tabel>'
        elif show_ok:
            msg += '没有发现更新的素材'
        nuke.message(utf8(msg))


def sent_to_dir(dir_):
    """Send current working file to dir."""

    copy(nuke.value('root.name'), dir_, threading=True)


def dropdata_handler(mime_type, data, from_dir=False):
    """Handling dropdata."""

    from wlf.notify import progress, CancelledError

    LOGGER.debug('Handling dropdata: %s %s', mime_type, data)
    if mime_type != 'text/plain':
        return
    data = u(data)

    def _isdir():
        if os.path.isdir(e(data)):
            _dirname = data.replace('\\', '/')
            filenames = nuke.getFileNameList(e(_dirname, 'UTF-8'))
            try:
                for filename in progress(filenames):
                    dropdata_handler(
                        mime_type, '{}/{}'.format(_dirname, filename),
                        from_dir=True)
            except CancelledError:
                pass
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
                b'read_from_file True '
                b'frame_rate 25 '
                b'suppress_dialog True '
                b'label {'
                b'导入的摄像机：\n'
                b'[basename [value file]]\n}')
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
        return PurePath(filename).name

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


def setup():
    if nuke.GUI:
        Localization.start_upate()
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(Localization.update)
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(warn_missing_frames)
    callback.CALLBACKS_ON_SCRIPT_SAVE.append(warn_missing_frames)
