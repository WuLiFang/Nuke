# -*- coding: UTF-8 -*-

import os
import re
import locale
from subprocess import call, Popen, PIPE, STDOUT

import nuke
import nukescripts

SYS_CODEC = locale.getdefaultlocale()[1]

class DropFrameCheck(object):
    dropframes_dict = {}
    dropframes_showed = []

    def __call__(self, ):
        self.check()
        
    def check(self):
        self.dropframes_showed = []
        for node in nuke.allNodes(group=nuke.Root()):
            self.getDropFrameRanges(node)
        self.show()
        
    def getDropFrameRanges(self, n=nuke.thisNode(), avoid=True):
        '''
        Return frameRanges of footage drop frame.
        
        @param n: node
        @param avoid: Avoid node that name endswith '_' for special use.
        @return frameranges
        '''
        # Avoid special node
        if avoid and n.name().endswith('_'):
            return None
        
        # Get dropframe ranges
        if n.Class() != 'Read' :
            return  False

        dropframe_list = []
        filename = nuke.filename(n)
        first = int(n['first'].value())
        last = int(n['last'].value())
        for frame in range(first, last + 1):
            filepath = self.getFileAtFrame(filename, frame).encode(SYS_CODEC)
            if not os.path.exists(filepath):
                dropframe_list.append(frame)
        
        frameranges = nuke.FrameRanges(dropframe_list)
        frameranges.compact()
        
        try:
            n['dropframes'].setValue(str(frameranges))
        except NameError:
            k = nuke.Text_Knob('dropframes', 'dropframes', str(frameranges))
            k.setFlag(nuke.INVISIBLE)
            n.addKnob(k)

        if not n['disable'].value() :
            self.dropframes_dict[filename] = frameranges

        return frameranges
        
    def getFileAtFrame(self, filename, frame):
        '''
        Return a frame mark expaned version of filename, with given frame
        '''
        pat = re.compile(r'%0?\d*d')
        formated_frame = lambda matchobj: matchobj.group(0) % frame
        return re.sub(pat, formated_frame, nukescripts.frame.replaceHashes(filename))

    def show(self, ):
        '''
        Show a dialog display all drop frames.
        '''
        if not nuke.env[ 'gui' ] :
            raise RuntimeWarning('this fucntion only work on gui mode')
        
        message_str = ''
        for file in self.dropframes_dict.keys() :
            frameranges = str(self.dropframes_dict[file])
            if frameranges and file not in self.dropframes_showed:
                self.dropframes_showed.append(file)
                message_str += '<tr><td>{}</td><td><span style=\"color:red\">{}</span></td></tr>'.format(file, frameranges)
        if message_str != '':
            message_str = '<style>td{padding:8px;}</style>'\
                          '<table>'\
                          '<tr><th>素材</th><th>缺帧</th></tr>'\
                          + message_str + \
                          '</table>'
            nuke.message(message_str)
        
    def addCallBack(self):
        nuke.addOnCreate(lambda : self.getDropFrameRanges(nuke.thisNode()), nodeClass='Read')
        nuke.addOnScriptSave(self.show)

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