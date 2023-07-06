# -*- coding=UTF-8 -*-
"""Nuke panels for comp.  """

from __future__ import absolute_import, print_function, unicode_literals

import wulifang.vendor.cast_unknown as cast
import nuke
import nukescripts  # type: ignore # pylint: disable=import-error

from wulifang._util import run_in_thread, run_in_main_thread

from . import batch
from .config import Config


class ConfigPanel(nukescripts.PythonPanel):
    def __init__(self):
        nukescripts.PythonPanel.__init__(
            self, cast.binary("单帧工程转换设置"), b"com.wlf.script_use_seq"
        )
        self.cfg = Config().read()

        self.knob_list = [
            (nuke.Multiline_Eval_String_Knob, "seq_include", cast.binary("序列查找规则")),
            (nuke.Multiline_Eval_String_Knob, "seq_exclude", cast.binary("序列排除规则")),
            (nuke.String_Knob, "override_project_directory", cast.binary("覆盖工程目录")),
            (nuke.Boolean_Knob, "use_wlf_write", cast.binary("使用 wlf_Write 替换 Write")),
            (nuke.Boolean_Knob, "is_auto_frame_range", cast.binary("自动设置工程帧范围")),
        ]
        for i in self.knob_list:
            k = i[0](i[1], i[2])
            try:
                k.setValue(self.cfg.get(i[1]))
            except TypeError:
                pass
            self.addKnob(k)
        for i in (
            "seq_include",
            "seq_exclude",
            "use_wlf_write",
            "is_auto_frame_range",
            "override_project_directory",
        ):
            self.knobs()[cast.binary(i)].setFlag(nuke.STARTLINE)

    def knobChanged(self, knob):
        """Override for buttons."""

        if knob is self.knobs()[b"OK"]:
            self.update_config()

    def update_config(self):
        """Write all setting to config."""

        for i in self.knob_list:
            if i[1] in self.cfg:
                self.cfg[i[1]] = self.knobs()[i[1]].value()


class BatchPanel(nukescripts.PythonPanel):
    """Dialog UI of class BatchComp."""

    def __init__(self):
        nukescripts.PythonPanel.__init__(
            self, cast.binary("批量单帧工程转换"), b"com.wlf.batch_script_use_seq"
        )
        self._shot_list = None
        self.cfg = Config().read()

        k = nuke.File_Knob(
            b"input_dir",
            cast.binary("输入文件夹"),
        )
        k.setValue(cast.binary(self.cfg.get("input_dir")))
        k.setFlag(nuke.STARTLINE)
        self.addKnob(k)
        k = nuke.File_Knob(
            b"output_dir",
            cast.binary("输出文件夹"),
        )
        k.setValue(cast.binary(self.cfg.get("output_dir")))
        k.setFlag(nuke.STARTLINE)
        self.addKnob(k)
        k = nuke.Script_Knob(
            b"setting",
            cast.binary("设置"),
        )
        k.setFlag(nuke.STARTLINE)
        self.addKnob(k)

    def knobChanged(self, knob):
        # type: (nuke.Knob) -> None
        """Override for buttons."""

        name = knob.name()

        if name == b"OK":
            self.confirm()

        if name == b"setting":
            _ = self.show_setting()

    @run_in_thread()
    @run_in_main_thread
    def show_setting(self):
        """Show comp setting."""

        ConfigPanel().showModalDialog()

    def update_config(self):
        """Write all setting to config."""

        self.cfg["input_dir"] = self.knobs()[b"input_dir"].value()
        self.cfg["output_dir"] = self.knobs()[b"output_dir"].value()

    def confirm(self):
        self.update_config()
        if not self.cfg["input_dir"] or not self.cfg["output_dir"]:
            nuke.message(cast.binary("未填写输入或输出文件夹"))
            raise RuntimeError("cancel")
        batch.run(self.cfg["input_dir"], self.cfg["output_dir"])
