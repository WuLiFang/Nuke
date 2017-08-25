# -*- coding: UTF-8 -*-
"""Deal with assets and files in nuke."""

import os
import re

import nuke

from .files import expand_frame, copy, get_encoded, get_unicode, is_ascii

__version__ = '0.3.16'


class DropFrameCheck(object):
    """Check drop frames and record on the node."""

    showed_files = []
    dropframes_dict = {}
    running = False

    def __init__(self, prefix=('_',)):
        self._prefix = prefix

    def start(self):
        """start one check."""
        if DropFrameCheck.running:
            return

        DropFrameCheck.running = True

        task = nuke.ProgressTask('检查缺帧')
        read_files = tuple((nuke.filename(n), n.frameRange())
                           for n in nuke.allNodes('Read') if not n['disable'].value())
        footages = {}
        for filename, framerange in read_files:
            footages.setdefault(filename, nuke.FrameRanges())
            footages[filename].add(framerange)
        dropframe_dict = {}
        all_num = len(footages)
        count = 0
        for filename, framerange in footages.items():
            if task.isCancelled():
                return
            if not filename:
                continue
            framerange.compact()

            task.setMessage(filename)
            task.setProgress(count * 100 // all_num)
            dropframes = self.dropframe_ranges(
                filename, framerange.toFrameList())
            if str(dropframes):
                dropframe_dict[filename] = dropframes
                nuke.executeInMainThread(DropFrameCheck.show_dialog)

            count += 1
        DropFrameCheck.dropframes_dict = dropframe_dict

        DropFrameCheck.running = False

    @staticmethod
    def dropframe_ranges(filename, framerange):
        """Return nuke framerange instance of dropframes."""
        assert isinstance(framerange, (list, nuke.FrameRange))
        filename = get_unicode(filename)
        task = nuke.ProgressTask(u'验证文件')
        ret = nuke.FrameRanges()
        if expand_frame(filename, 1) == filename:
            if not os.path.isfile(get_encoded(filename)):
                ret.add(framerange)
            return ret

        folder = os.path.dirname(filename)
        if not os.path.isdir(get_encoded(folder)):
            ret.add(framerange)
            return ret
        _listdir = list(get_unicode(i)
                        for i in os.listdir(get_encoded(folder)))
        all_num = len(framerange)
        count = 0
        for f in framerange:
            task.setProgress(count * 100 // all_num)
            frame_file = unicode(os.path.basename(expand_frame(filename, f)))
            task.setMessage(frame_file)
            if frame_file not in _listdir:
                ret.add([f])
            count += 1
        ret.compact()
        return ret

    @classmethod
    def show_dialog(cls, show_all=False):
        """Show all dropframes to user."""
        message = ''
        for filename, dropframes in cls.dropframes_dict.items():
            if not show_all\
                    and filename in cls.showed_files:
                continue
            if dropframes:
                message += '<tr><td><span style=\"color:red\">{}</span>'\
                    '</td><td>{}</td></tr>'.format(dropframes, filename)
                cls.showed_files.append(filename)

        if message:
            message = '<style>td{padding:8px;}</style>'\
                '<table>'\
                '<tr><th>缺帧</th><th>素材</th></tr>'\
                + message +\
                '</table>'
            nuke.message(message)


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
            task = nuke.ProgressTask(data)
            _dirname = data.replace('\\', '/')
            filenames = nuke.getFileNameList(get_encoded(_dirname, 'UTF-8'))
            all_num = len(filenames)
            for index, filename in enumerate(filenames):
                if task.isCancelled():
                    return True
                task.setMessage(filename)
                task.setProgress(index * 100 // all_num)
                dropdata_handler(
                    mime_type, '{}/{}'.format(_dirname, filename), from_dir=True)
            return True

    def _ignore():
        ignore_pat = (r'thumbs\.db$', r'.*\.lock$', r'.* - 副本\b')
        filename = os.path.basename(data)
        for pat in ignore_pat:
            if re.match(get_unicode(pat), get_unicode(filename), flags=re.I | re.U):
                return True

    def _file_protocol():
        match = re.match(r'file:///([^/].*)', data)
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
                'label {{[value this.vfield_file]}}'.format(data=data))
            return True

    def _nk():
        if data.endswith('.nk'):
            nuke.scriptReadFile(data)
            return True

    def _video():
        if data.endswith(('.mov', '.mp4', '.avi')):
            # Avoid mov reader bug.
            if not is_ascii(data):
                n = nuke.createNode(
                    'Read', 'disable true label "{0}\n**不支持非英文路径**"'.format(data))
            else:
                n = nuke.createNode('Read', 'file "{}"'.format(data))
            if n.hasError():
                n['disable'].setValue(True)
            return True

    def _from_dir():
        if from_dir:
            n = nuke.createNode('Read', 'file "{}"'.format(data))
            if n.hasError():
                n['disable'].setValue(True)
            return True

    for func in (_isdir, _ignore, _from_dir, _file_protocol, _video, _vf, _nk):
        if func():
            return True
