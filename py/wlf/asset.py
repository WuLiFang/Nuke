# -*- coding: UTF-8 -*-
"""Deal with assets and files."""

import locale
import os
import re
import threading
import time
import shutil

import nuke

SYS_CODEC = locale.getdefaultlocale()[1]


class DropFrameCheck(threading.Thread):
    """Check drop frames and record on the node."""

    # lock = threading.Lock()
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
        if self._node['disable'].value():
            return
        # self.lock.acquire()
        while self._node:
            time.sleep(5)
            self.record()
        # self.lock.release()

    def dropframe_ranges(self):
        """Return nuke framerange instance of dropframes."""

        _filename = nuke.filename(self._node)
        ret = nuke.FrameRanges()
        if not self._node \
                or not _filename \
                or self._node.name().startswith(self._prefix)\
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
            nuke.executeInMainThreadWithResult(_set_knob)

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


def main():
    """For test script effect."""

    n = nuke.toNode('Read3')
    result = DropFrameCheck(n).dropframe_ranges()
    print(result)


if __name__ == '__main__':
    # For test in script editor.
    main()
