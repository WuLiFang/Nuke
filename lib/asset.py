# -*- coding: UTF-8 -*-
"""Deal with assets and files in nuke."""

import os
import re
import time
import logging
import multiprocessing.dummy as multiprocessing

import nuke

from wlf.files import copy
from wlf.path import expand_frame, get_encoded, get_unicode, is_ascii
from wlf.notify import Progress, CancelledError

from node import Last

__version__ = '0.5.5'

LOGGER = logging.getLogger('com.wlf.asset')


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
    def update(cls, nodes=None):
        """update self."""
        if isinstance(nodes, nuke.Node):
            nodes = [nodes]
        nodes = nodes or nuke.allNodes('Read')
        if not nodes:
            return

        footages = get_footages(nodes)

        def _check(filename):
            framerange = footages[filename]
            framerange.compact()
            dropframes = get_dropframe(filename, framerange.toFrameList())
            if str(dropframes):
                cls._file_dropframe[filename] = dropframes
            elif cls._file_dropframe.has_key(filename):
                del cls._file_dropframe[filename]
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


def warn_mtime(show_dialog=False, show_ok=False):
    """Show footage that mtime newer than script mtime. """
    msg = ''
    newer_footages = {}
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
        filename = nuke.filename(n)
        ret.setdefault(filename, nuke.FrameRanges())
        ret[filename].add(n.frameRange())
    return ret


def get_dropframe(filename, framerange):
    """Return dropframes for @filename in @framerange. -> nuke.FrameRanges """
    assert isinstance(framerange, (list, nuke.FrameRange))
    filename = get_unicode(filename)
    dir_path = os.path.dirname(filename)

    task = Progress(u'验证文件', total=len(framerange))
    ret = nuke.FrameRanges()
    if not os.path.isdir(get_encoded(dir_path)) or \
        (expand_frame(filename, 1) == filename
         and not os.path.isfile(get_encoded(filename))):
        ret.add(framerange)
        return ret

    files = os.listdir(get_encoded(dir_path))
    basename = os.path.basename(filename)
    for f in framerange:
        frame_file = expand_frame(basename, f)
        task.step(frame_file)
        if get_encoded(frame_file) not in files:
            ret.add([f])
    ret.compact()
    return ret


def sent_to_dir(dir_):
    """Send current working file to dir."""
    copy(nuke.value('root.name'), dir_)


def dropdata_handler(mime_type, data, from_dir=False):
    """Handling dropdata."""
    # print(mime_type, data)
    if mime_type != 'text/plain':
        return
    data = get_unicode(data)

    def _isdir():
        if os.path.isdir(get_encoded(data)):
            _dirname = data.replace('\\', '/')
            filenames = nuke.getFileNameList(get_encoded(_dirname, 'UTF-8'))
            task = Progress(data, total=len(filenames))
            for filename in filenames:
                try:
                    task.step(filename)
                except CancelledError:
                    return True
                read_node = dropdata_handler(
                    mime_type, '{}/{}'.format(_dirname, filename), from_dir=True)
                if isinstance(read_node, nuke.Node):
                    DropFrames.update(read_node)
            return True

    def _ignore():
        ignore_pat = (r'thumbs\.db$', r'.*\.lock$', r'.* - 副本\b')
        filename = os.path.basename(data)
        for pat in ignore_pat:
            if re.match(get_unicode(pat), get_unicode(filename), flags=re.I | re.U):
                return True
        if from_dir and not is_ascii(data):
            nuke.createNode(
                'StickyNote', 'autolabel {{\'<div align="center">\'+autolabel()+\'</div>\'}} '
                'label {{{}\n\n<span style="color:red;text-align:center;font-weight:bold">'
                '不支持非英文路径</span>}}'.format(data), inpanel=False)
            return True

    def _file_protocol():
        match = re.match(r'file:///([^/].*)', data)
        if match:
            _data = match.group(1)
            return dropdata_handler(mime_type, _data)

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
            if n.hasError():
                n['disable'].setValue(True)
            return n

    for func in (_isdir, _ignore, _file_protocol, _video, _vf, _fbx, _from_dir, _nk):
        ret = func()
        if ret:
            return ret


def check_localization_support(func):
    """Decorator.  """
    def _func(*args, **kwargs):
        if nuke.env['NukeVersionMajor'] < 10:
            print('Localization update only support Nuke10.0 or above.')
            return
        func(*args, **kwargs)
    _func.__name__ = func.__name__
    _func.__doc__ = func.__doc__
    return _func


class Localization(object):
    """Nuke localization utility.  """
    lock = multiprocessing.Lock()

    @classmethod
    @check_localization_support
    def start_upate(cls, interval=1800):
        """Start update thread"""

        def _func():
            LOGGER.debug(u'Thread start: com.wlf.UpdateLocalization')
            time.sleep(interval)
            while cls.lock.acquire(False):
                LOGGER.debug(u'Localization.update from thread')
                nuke.executeInMainThread(cls.update)
                cls.lock.release()
                time.sleep(interval)
        proc = multiprocessing.Process(
            target=_func, name='com.wlf.UpdateLocalization')
        proc.setDaemon(True)
        proc.start()

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
