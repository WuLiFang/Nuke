# -*- coding=UTF-8 -*-
"""Split all-in-one exr to multiple files."""
import os
import re
import sys
import threading
import argparse
from subprocess import Popen


import nuke
import nukescripts

from wlf.progress import Progress
from wlf.files import url_open, get_footage_name, get_encoded

__version__ = '0.1.0'


class Dialog(nukescripts.PythonPanel):
    """Dialog UI of class Comp."""

    knob_list = [
        (nuke.Tab_Knob, 'general_setting', '常用设置'),
        (nuke.File_Knob, 'input_dir', '输入文件夹'),
        (nuke.File_Knob, 'output_dir', '输出文件夹'),
        (nuke.Enumeration_Knob, 'output_ext', '输出格式',
         ['exr', 'png', 'tga', 'jpg', 'mov']),
        (nuke.Tab_Knob, 'filter', '正则过滤'),
        (nuke.String_Knob, 'footage_pat', '素材名'),
        (nuke.String_Knob, 'dir_pat', '路径'),
        (nuke.EndTabGroup_Knob, 'end_tab', ''),
        (nuke.Multiline_Eval_String_Knob, 'info', ''),
    ]
    default = {
        'footage_pat': '.+\\.exr[ 0-9-]*',
        'output_ext': 'exr',
        'output_dir': 'E:/splitexr'
    }

    def __init__(self):
        nukescripts.PythonPanel.__init__(self, '吾立方批量合成', 'com.wlf.multicomp')
        self._files = []

        for i in self.knob_list:
            k = i[0](i[1], *i[2:])
            try:
                k.setValue(self.default.get(i[1]))
            except TypeError:
                pass
            self.addKnob(k)
        self.update()

    def knobChanged(self, knob):
        """Overrride for buttons."""

        if knob is self.knobs()['OK']:
            threading.Thread(target=self.progress).start()
        else:
            self.update()

    @property
    def input_dir(self):
        """Input footage directory. """
        return self.knobs()['input_dir'].value()

    @property
    def output_dir(self):
        """Output save path. """
        return self.knobs()['output_dir'].value()

    @property
    def output_ext(self):
        """Output file type.  """
        return self.knobs()['output_ext'].value()

    @property
    def footage_pat(self):
        """Footage regular expression match pattern. """
        return self.knobs()['footage_pat'].value()

    @property
    def dir_pat(self):
        """Directory regular expression match pattern. """
        return self.knobs()['dir_pat'].value()

    def files(self):
        """Return files in input dir. """
        ret = []

        if not os.path.isdir(self.input_dir):
            return ret
        dirs = list(x[0] for x in os.walk(self.input_dir))
        for dir_ in dirs:
            # Get footage in subdir
            if not re.match(self.dir_pat, os.path.basename(dir_.rstrip('\\/'))):
                continue

            footages = [i for i in nuke.getFileNameList(dir_) if
                        not i.endswith(('副本', '.lock'))]
            if footages:
                for f in footages:
                    if os.path.isdir(os.path.join(dir_, f)):
                        continue
                    if re.match(self.footage_pat, f, flags=re.I):
                        ret.append(f)
        ret.sort()
        self._files = ret
        return ret

    def update(self):
        """Update ui info and button enabled."""
        files = self.files()

        def _info():
            info = u'测试'
            if files:
                info = u'# 共{}个素材\n'.format(len(files))
                info += u'\n'.join(files)
            else:
                info = u'找不到素材'
            self.knobs()['info'].setValue(info)

        def _button_enabled():

            k = self.knobs().get('OK')
            if k:
                if files:
                    k.setEnabled(True)
                else:
                    k.setEnabled(False)

        _info()
        _button_enabled()

    def progress(self):
        """Start process all shots with a processbar."""

        task = Progress('分离exr')

        files = self._files
        all_num = len(files)
        for i, f in enumerate(files):
            task.set(i * 100 // all_num, f)

            cmd = u'"{nuke}" -t "{script}" "{file_path}" "{output_dir}" "{file_type}"'.format(
                nuke=nuke.EXE_PATH,
                script=__file__,
                file_path=os.path.join(self.input_dir, f),
                file_type=self.output_ext,
                output_dir=self.output_dir
            )
            proc = Popen(get_encoded(cmd))
            proc.wait()

        url_open(self.output_dir, isfile=True)

    @staticmethod
    def show():
        """Show a dialog for user using this class."""

        Dialog().showModalDialog()


def split(file_path, output_dir, file_type=None):
    """Render splited files.  """
    file_path = get_encoded(file_path, 'UTF-8')
    output_dir = get_encoded(output_dir, 'UTF-8')

    n = nuke.nodes.Read()
    read_node = n
    n['file'].fromUserText(file_path)
    path = n['file'].value()
    ext = u'.' + file_type or os.path.splitext(path)[1]
    basename = get_footage_name(os.path.basename(path))
    for layer in nuke.layers(n):
        _kwarg = {'in': layer}  # Avoid use of python keyword 'in'.
        n = nuke.nodes.Shuffle(inputs=[read_node], label=layer, **_kwarg)
        if file_type == 'mov':
            filename = '{}.{}{}'.format(basename, layer, ext)
        elif n.firstFrame() == n.lastFrame():
            filename = os.path.basename(file_path)
        else:
            filename = '{}.{}.%04d{}'.format(basename, layer, ext)
        output = os.path.join(output_dir, basename, layer, filename)
        n = nuke.nodes.Write(inputs=[n], channels='rgba')
        n['file'].fromUserText(output)

    nuke.render(nuke.Root(), start=n.firstFrame(),
                end=n.lastFrame(), continueOnError=True)


def main():
    """Script entrance.  """
    split(*sys.argv[1:])


def _argparse():
    # TODO
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input file')
    parser.add_argument('output_dir', help='input file')
    return parser.parse_args()


if __name__ == '__main__':
    main()
