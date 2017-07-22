# -*- coding: UTF-8 -*-
"""Deal with assets and files."""

import locale
import os
import re
import threading
import time
import shutil

import nuke

__version__ = '0.2.7'
SYS_CODEC = locale.getdefaultlocale()[1]


class DropFrameCheck(threading.Thread):
    """Check drop frames and record on the node."""

    lock = threading.Lock()
    showed_files = []
    knob_name = 'dropframes'

    def __init__(self, n, prefix=('_',)):
        threading.Thread.__init__(self)
        self.daemon = True
        self._node = n
        self._prefix = prefix

    @property
    def knob_tcl_name(self):
        """Custom knob name."""
        if self._node:
            return '{}.{}'.format(self._node.name(), self.knob_name)

    def run(self):
        time.sleep(5)
        try:
            if not self._node or self._node['disable'].value():
                return
        except ValueError:
            return
        with self.lock:
            self.record()
        DropFrameCheck(self._node).start()

    def dropframe_ranges(self):
        """Return nuke framerange instance of dropframes."""
        ret = nuke.FrameRanges()
        if not self._node\
                or self._node.name().startswith(self._prefix):
            return ret
        _filename = nuke.filename(self._node)
        if not _filename \
                or expand_frame(_filename, 1) == _filename:
            return ret

        _read_framerange = xrange(
            self._node.firstFrame(), self._node.lastFrame() + 1)
        for f in _read_framerange:
            _file = expand_frame(_filename, f)
            if not os.path.isfile(unicode(_file, 'UTF-8').encode(SYS_CODEC)):
                ret.add([f])
        ret.compact()
        return ret

    def setup_node(self):
        """Add knob if needed."""

        def _add_knob():
            k = nuke.String_Knob(self.knob_name, '缺帧')
            k.setEnabled(False)
            self._node.addKnob(k)

        if not nuke.exists(self.knob_tcl_name):
            nuke.executeInMainThreadWithResult(_add_knob)

    def record(self):
        """Record dropframes on knob for futher use."""

        _dropframes = str(self.dropframe_ranges())

        def _set_knob():
            self._node['dropframes'].setValue(_dropframes)
            if _dropframes:
                nuke.warning('{}: [dropframnes]{}'.format(
                    self._node.name(), _dropframes))
        if _dropframes != nuke.value(self.knob_tcl_name, ''):
            self.setup_node()
            nuke.executeInMainThread(_set_knob)

    @classmethod
    def show_dialog(cls, show_all=False):
        """Show all dropframes to user."""

        _message = ''
        for n in nuke.allNodes('Read'):
            _filename = nuke.filename(n)
            if not show_all:
                if _filename in cls.showed_files:
                    continue
            _dropframes = nuke.value(
                '{}.{}'.format(n.name(), cls.knob_name), '')
            if _dropframes:
                _message += '<tr><td>{}</td><td>'\
                    '<span style=\"color:red\">{}</span></td></tr>'.format(
                        _filename, _dropframes)
                cls.showed_files.append(_filename)

        if _message:
            _message = '<style>td{padding:8px;}</style>'\
                '<table>'\
                '<tr><th>素材</th><th>缺帧</th></tr>'\
                + _message + \
                '</table>'
            nuke.message(_message)


def expand_frame(filename, frame):
    '''
    Return a frame mark expaned version of filename, with given frame
    '''
    def _format_repl(matchobj):
        return matchobj.group(0) % frame

    def _hash_repl(matchobj):
        return '%0{}d'.format(len(matchobj.group(0)))
    ret = filename
    ret = re.sub(r'(\#+)', _hash_repl, ret)
    ret = re.sub(r'(%0?\d*d)', _format_repl, ret)
    return ret


def sent_to_dir(dir_):
    """Send current working file to dir."""
    copy(nuke.value('root.name'), dir_)


def copy(src, dst):
    """Copy src to dst."""
    message = u'{} -> {}'.format(src, dst)
    print(message)
    nuke.tprint(message)
    if not os.path.exists(src):
        return
    dst_dir = os.path.dirname(dst)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    shutil.copy2(src, dst)


def dropdata_handler(mime_type, data, from_dir=False):
    """Handling dropdata."""
    # print(mime_type, data)
    if mime_type != 'text/plain':
        return
    match = re.match(r'file:///([^/].*)', data)

    if os.path.isdir(data):
        _dirname = data.replace('\\', '/')
        for i in nuke.getFileNameList(_dirname):
            dropdata_handler(
                mime_type, '{}/{}'.format(_dirname, i), from_dir=True)
    elif os.path.basename(data).lower() == 'thumbs.db':
        pass
    elif match:
        data = match.group(1)
        return dropdata_handler(mime_type, data, from_dir=True)
    elif data.endswith('.fbx'):
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
    elif data.endswith('.vf'):
        nuke.createNode(
            'Vectorfield',
            'vfield_file "{data}" '
            'file_type vf '
            'label {{[value this.vfield_file]}}'.format(data=data))
    elif data.endswith('.nk'):
        nuke.scriptReadFile(data)
    elif from_dir:
        n = nuke.createNode('Read', 'file "{}"'.format(data))
    else:
        return
    return True
