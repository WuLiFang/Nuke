# -*- coding=UTF-8 -*-
"""Split all-in-one exr to multiple files."""
from __future__ import absolute_import, print_function, unicode_literals

import argparse
import os
import re
import sys
import webbrowser
from subprocess import Popen

try:
    _argv = sys.argv  # Nuke will reset sys.argv
    import nuke

    from nuketools import utf8
    from wlf.decorators import run_async
    from wlf.progress import progress
    from wlf.codectools import get_encoded as e
    from wlf.path import PurePath, Path
except:
    raise


if nuke.GUI:
    import nukescripts  # pylint: disable=import-error

    class Dialog(nukescripts.PythonPanel):
        """Dialog UI of splitexr."""

        knob_list = [
            (nuke.Tab_Knob, 'general_setting', b'常用设置'),
            (nuke.File_Knob, 'input_dir', b'输入文件夹'),
            (nuke.File_Knob, 'output_dir', b'输出文件夹'),
            (nuke.Enumeration_Knob, 'output_ext', b'输出格式',
             ['exr', 'png', 'tga', 'jpg', 'mov']),
            (nuke.Tab_Knob, 'filter', b'正则过滤'),
            (nuke.String_Knob, 'footage_pat', b'素材名'),
            (nuke.String_Knob, 'dir_pat', b'路径'),
            (nuke.EndTabGroup_Knob, 'end_tab', ''),
            (nuke.Multiline_Eval_String_Knob, 'info', ''),
        ]
        default = {
            'footage_pat': '.+\\.exr[ 0-9-]*',
            'output_ext': 'exr',
            'output_dir': 'E:/splitexr'
        }

        def __init__(self):
            nukescripts.PythonPanel.__init__(
                self, b'分离exr', 'com.wlf.splitexr')
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
                self.execute()
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

                footages = [i for i in nuke.getFileNameList(dir_, True) if
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
                info = '测试'
                if files:
                    info = '# 共{}个素材\n'.format(len(files))
                    info += '\n'.join(files)
                else:
                    info = '找不到素材'
                self.knobs()['info'].setValue(utf8(info))

            def _button_enabled():

                k = self.knobs().get('OK')
                if k:
                    if files:
                        k.setEnabled(True)
                    else:
                        k.setEnabled(False)

            _info()
            _button_enabled()

        @run_async
        def execute(self):
            """Start task.  """

            files = self._files
            for f in progress(files, '分离exr'):
                cmd = u'"{nuke}" -t "{script}" "{file_path}" "{output_dir}" -f "{file_type}"'.format(
                    nuke=nuke.EXE_PATH,
                    script=__file__,
                    file_path=os.path.join(self.input_dir, f),
                    file_type=self.output_ext,
                    output_dir=self.output_dir
                )
                proc = Popen(e(cmd))
                proc.wait()

            webbrowser.open(self.output_dir)

        @staticmethod
        def show():
            """Show a dialog for user using this class."""

            Dialog().showModalDialog()


def split(filename, output_dir, file_format=None):
    """Render splited files.  """

    path = PurePath(re.sub(r' [\d -]*$', '', filename))
    output_dir = Path(output_dir)

    # Create read node.
    read_node = nuke.nodes.Read()
    read_node['file'].fromUserText(filename)
    if file_format:
        assert isinstance(file_format, (str, unicode))
        suffix = '.{}'.format(file_format.strip('.'))
    else:
        suffix = path.suffix or '.mov'

    # Get layers for render.
    layers = nuke.layers(read_node)
    assert isinstance(layers, list)
    layers_overlap = {
        'rgba': ('rgb', 'alpha')
    }
    for k, v in layers_overlap.items():
        if k in layers:
            for i in v:
                try:
                    layers.remove(i)
                except ValueError:
                    pass

    # Create write nodes.
    for layer in layers:
        _kwargs = {'in': layer}  # Avoid use of python keyword 'in'.
        n = nuke.nodes.Shuffle(inputs=[read_node], label=layer, **_kwargs)
        n = nuke.nodes.Write(inputs=[n],
                             file=((output_dir
                                    / '{}.{}{}'.format(path.stem, layer, suffix))
                                   .as_posix()),
                             channels='rgba')

    # Render.
    output_dir.mkdir(parents=True, exist_ok=True)
    nuke.render(nuke.Root(),
                start=read_node.firstFrame(),
                end=read_node.lastFrame())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='输入文件')
    parser.add_argument('output_dir', help='输出路径')
    parser.add_argument('-f', '--format', help='输出文件类型')
    args = parser.parse_args(_argv[1:])

    split(args.input, args.output_dir, args.format)


if __name__ == '__main__':
    main()
