# -*- coding: UTF-8 -*-

import os
import re
import locale
import threading
from subprocess import call, Popen, PIPE, STDOUT

import nuke
import nukescripts

SYS_CODEC = locale.getdefaultlocale()[1]

class DropFrameCheck(threading.Thread):
    knob_name = 'dropframes'
    lock = threading.Lock()
    showed_files = []

    def __init__(self, n, prefix=('_',)):
        threading.Thread.__init__(self)
        self.daemon = True
        self._node = n
        self._prefix = prefix
        self._knob_tcl_name = '{}.{}'.format(self._node.name(), self.knob_name)
        
    def run(self):
        self.lock.acquire()
        self.setup_node()
        self.record()
        self.lock.release()
        
    def dropframe_ranges(self):
        _ret = nuke.FrameRanges()
        if self._node.name().startswith(self._prefix):
            return _ret
        
        _read_framerange = self._node.frameRange()
        for f in _read_framerange:
            _file = self.expand_frame(nuke.filename(self._node), f)
            if not os.path.isfile(_file):
                _ret.add([f])
        _ret.compact()
        return _ret

    def setup_node(self):
        def _add_knob():
                k = nuke.String_Knob(self.knob_name, '缺帧')
                k.setEnabled(False)
                self._node.addKnob(k)

        if not nuke.exists(self._knob_tcl_name):
            nuke.executeInMainThreadWithResult(_add_knob)

    def record(self):
        _dropframes = str(self.dropframe_ranges())
        def _set_knob():
            self._node['dropframes'].setValue(_dropframes)
            if not self._node['disable'].value():
                nuke.warning('{}: [缺帧]{}'.format(self._node.name(), _dropframes))
        if _dropframes != self._node[self.knob_name].value():
            nuke.executeInMainThreadWithResult(_set_knob)
        
    def expand_frame(self, filename, frame):
        '''
        Return a frame mark expaned version of filename, with given frame
        '''
        pat = re.compile(r'%0?\d*d')
        formated_frame = lambda matchobj: matchobj.group(0) % frame
        return re.sub(pat, formated_frame, nukescripts.frame.replaceHashes(filename))
    
    @classmethod
    def show_dialog(self, show_all=False):
        _message = ''
        for n in nuke.allNodes('Read'):
            _filename = nuke.filename(n)
            if not show_all:
                if _filename in self.showed_files:
                    continue
            _dropframes = nuke.value('{}.{}'.format(n.name(),self.knob_name), '')
            if _dropframes:
                _message += '<tr><td>{}</td><td><span style=\"color:red\">{}</span></td></tr>'.format(_filename, _dropframes)
                self.showed_files.append(_filename)
                
        if _message:
            _message = '<style>td{padding:8px;}</style>'\
                '<table>'\
                '<tr><th>素材</th><th>缺帧</th></tr>'\
                + _message + \
                '</table>'
            nuke.message(_message)

def sent_to_dir(dir):
    if not nuke.value('root.name'):
        return False

    if os.path.isdir(dir):
        src = '"{}"'.format(os.path.normcase(nuke.scriptName()))
        dst = '"{}\\"'.format(dir.strip('"').rstrip('/\\'))
        cmd = ' '.join(['XCOPY', '/Y', '/D', '/I', '/V', src, dst])
        print(repr(cmd))
        _proc = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        print(_proc.communicate()[0])
    else:
        return False

if __name__ == '__main__':
    # For test in script editor.
    try:
        n = nuke.toNode('Read3')
        result = DropFrameCheck(n).dropframe_ranges()
        print(result)
    except:
        import traceback
        traceback.print_exc()