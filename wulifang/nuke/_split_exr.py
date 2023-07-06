# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import os
import re
import webbrowser
from subprocess import Popen
import time


import nuke

from wulifang._util import (
    cast_str,
    cast_text,
    run_in_thread,
    JSONStorageItem,
    remove_prefix,
    run_in_main_thread,
    remove_frame_placeholder,
)
from wulifang.nuke._util import (
    Progress,
    Panel as _Panel,
    create_knob,
    create_node,
    knob_of,
    parse_file_input,
)


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


_INPUT_DIR = JSONStorageItem(
    "inputDir@9db46f65-3ff5-4ba0-aafd-c92f17869498", lambda: ""
)
_INPUT_DIR_REGEX = JSONStorageItem(
    "inputDirRegex@9db46f65-3ff5-4ba0-aafd-c92f17869498", lambda: ""
)
_INPUT_FILE_REGEX = JSONStorageItem(
    "inputFileRegex@9db46f65-3ff5-4ba0-aafd-c92f17869498", lambda: r".*\.exr$"
)
_OUTPUT_DIR = JSONStorageItem(
    "outputDir@9db46f65-3ff5-4ba0-aafd-c92f17869498", lambda: ""
)
_OUTPUT_EXT = JSONStorageItem(
    "outputExt@9db46f65-3ff5-4ba0-aafd-c92f17869498", lambda: ".exr"
)


class Panel(_Panel):
    def __init__(self):
        _Panel.__init__(
            self,
            cast_str("分离 EXR"),
            cast_str("com.wlf-studio.split-exr"),
        )
        self._files = []  # type: list[str]
        self.addKnob(
            create_knob(
                nuke.Tab_Knob,
                "basic",
                label="基本",
            )
        )

        self._input_dir_knob = create_knob(
            nuke.File_Knob,
            "input_dir",
            label="输入文件夹",
            value=cast_str(_INPUT_DIR.get()),
        )
        self.addKnob(self._input_dir_knob)

        self._output_dir_knob = create_knob(
            nuke.File_Knob,
            "output_dir",
            label="输出文件夹",
            value=cast_str(_OUTPUT_DIR.get()),
        )
        self.addKnob(self._output_dir_knob)

        self._output_ext_knob = nuke.Enumeration_Knob(
            cast_str("output_ext"),
            cast_str("输出文件格式"),
            (
                cast_str(".exr"),
                cast_str(".png"),
                cast_str(".tga"),
                cast_str(".jpg"),
                cast_str(".mov"),
            ),
        )
        self._output_ext_knob.setValue(cast_str(_OUTPUT_EXT.get()))
        self.addKnob(self._output_ext_knob)

        self.addKnob(create_knob(nuke.Tab_Knob, "filter", label="正则过滤"))

        self._input_dir_regex_knob = create_knob(
            nuke.String_Knob,
            "input_dir_regex",
            label="目录名",
            value=cast_str(_INPUT_DIR_REGEX.get()),
        )
        self.addKnob(self._input_dir_regex_knob)

        self._input_file_regex_knob = create_knob(
            nuke.String_Knob,
            "input_file_regex",
            label="文件名",
            value=cast_str(_INPUT_FILE_REGEX.get()),
        )
        self.addKnob(self._input_file_regex_knob)

        self.addKnob(create_knob(nuke.EndTabGroup_Knob, ""))

        self._info_knob = create_knob(
            nuke.Multiline_Eval_String_Knob,
            "info",
            "",
        )
        self.addKnob(self._info_knob)

        self.update()

    def addKnob(self, k):
        # type: (nuke.Knob) -> None
        _Panel.addKnob(self, k)
        if k is self._ok_knob:
            self.update()

    @property
    def _ok_knob(self):
        return self.knobs().get(cast_str("OK"))

    def knobChanged(self, knob):
        # type: (nuke.Knob) -> None
        """Override for buttons."""

        if knob is self._input_dir_regex_knob:
            _INPUT_DIR_REGEX.set(cast_text(self._input_dir_regex_knob.value()))
            self.update()
        elif knob is self._input_file_regex_knob:
            _INPUT_FILE_REGEX.set(cast_text(self._input_file_regex_knob.value()))
            self.update()
        elif knob is self._input_dir_knob:
            _INPUT_DIR.set(cast_text(self._input_dir_knob.value()))
            self.update()
        elif knob is self._output_dir_knob:
            _OUTPUT_DIR.set(cast_text(self._output_dir_knob.value()))
            self.update()
        elif knob is self._output_ext_knob:
            _OUTPUT_EXT.set(cast_text(self._output_ext_knob.value()))
            self.update()
        elif knob is self._ok_knob:
            self.execute()

    def _iter_files(self):
        input_dir = _INPUT_DIR.get()
        if not os.path.isdir(input_dir):
            return
        input_dir_regex = _INPUT_DIR_REGEX.get()
        input_file_regex = _INPUT_FILE_REGEX.get()
        for dirpath, _dirnames, _filenames in os.walk(input_dir):
            # Get footage in subdir
            if not re.match(input_dir_regex, os.path.basename(dirpath)):
                continue

            for i in nuke.getFileNameList(
                cast_str(dirpath),
                True,
                False,
                False,
            ):
                v = parse_file_input(cast_text(i))
                print("name", v.name())
                if v.name().endswith(("副本", ".lock")):
                    continue
                if not re.match(input_file_regex, v.name(), flags=re.I):
                    continue
                yield os.path.join(dirpath, v.raw()).replace("\\", "/")

    def update(self):
        """Update ui info and button enabled."""

        files = sorted(self._iter_files())
        self._files = files

        input_dir = _INPUT_DIR.get()
        output_dir = _OUTPUT_DIR.get()

        def info():
            if not files:
                yield "# 无输入序列，请检查设置"
                return
            yield "# 共{}个输入序列\n".format(len(files))
            for i in files:
                yield remove_prefix(i, input_dir).lstrip("/")

        self._info_knob.setValue(cast_str("\n".join(info())))

        if self._ok_knob:
            self._ok_knob.setEnabled(bool(files and output_dir))

    @run_in_thread("split-exr")
    def execute(self):
        """Start task."""

        files = self._files
        input_dir = _INPUT_DIR.get()
        output_ext = _OUTPUT_EXT.get()
        output_dir = _OUTPUT_DIR.get()
        if not output_dir:
            run_in_main_thread(nuke.message)(cast_str("输出目录为必填"))
            return

        with Progress("拆分 EXR", estimate_secs=300.0 * len(files)) as p:
            for f in files:
                p.set_message(f)
                p.increase()
                proc = Popen(
                    (
                        cast_text(nuke.EXE_PATH),
                        "-t",
                        __file__,
                        os.path.join(input_dir, f),
                        output_dir,
                        "-t",
                        output_ext,
                    ),
                )

                try:
                    while proc.poll() is None:
                        time.sleep(0.1)
                        p.increase()
                except Progress.Cancelled:
                    proc.kill()
                    raise

        webbrowser.open(output_dir)


def dialog():
    Panel().showModalDialog()


def split(input_file, output_dir, output_ext):
    # type: (Text, Text, Text) -> None
    read_node = create_node("Read")
    knob_of(read_node, "file", nuke.File_Knob).fromUserText(cast_str(input_file))

    # Get layers for render.
    layers = list(map(cast_text, nuke.layers(read_node)))
    assert isinstance(layers, list)
    layers_overlap = {"rgba": ("rgb", "alpha")}
    for k, v in layers_overlap.items():
        if k in layers:
            for i in v:
                try:
                    layers.remove(i)
                except ValueError:
                    pass

    input_basename = os.path.basename(input_file)
    output_name, _ = os.path.splitext(input_basename)
    if output_ext in (".mov"):
        output_name = remove_frame_placeholder(output_name)

    # Create write nodes.
    for layer in layers:
        n = create_node(
            "Shuffle",
            "in %s" % (layer,),
            label=layer,
            inputs=(read_node,),
        )
        n = create_node(
            "Write",
            "file %s\nchannels rgba"
            % (
                (
                    "%s/%s.%s/%s.%s%s"
                    % (
                        output_dir,
                        remove_frame_placeholder(output_name),
                        layer,
                        output_name,
                        layer,
                        output_ext,
                    )
                ).replace("\\", "/"),
            ),
            inputs=(n,),
        )

    nuke.render(nuke.Root(), start=read_node.firstFrame(), end=read_node.lastFrame())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="输入文件表达式")
    parser.add_argument("output_dir", help="输出路径")
    parser.add_argument("-t", "--output-ext", help="输出文件类型")
    args = parser.parse_args([cast_text(i) for i in nuke.rawArgs[3:]])

    split(cast_text(args.input), cast_text(args.output_dir), cast_text(args.output_ext))


if __name__ == "__main__":
    main()
