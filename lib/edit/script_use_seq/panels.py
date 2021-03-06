# -*- coding=UTF-8 -*-
"""Nuke panels for comp.  """

from __future__ import absolute_import, print_function, unicode_literals

import nuke
import nukescripts  # type: ignore # pylint: disable=import-error

from nuketools import iutf8, utf8
from wlf.decorators import run_async, run_in_main_thread

from . import batch
from .config import Config


class ConfigPanel(nukescripts.PythonPanel):
    def __init__(self):
        nukescripts.PythonPanel.__init__(
            self, utf8('单帧工程转换设置'), 'com.wlf.script_use_seq')
        self.cfg = Config().read()

        self.knob_list = [
            (nuke.Multiline_Eval_String_Knob,
             'seq_include', utf8('序列查找规则')),
            (nuke.Multiline_Eval_String_Knob,
             'seq_exclude', utf8('序列排除规则')),
            (nuke.String_Knob, 'override_project_directory', utf8('覆盖工程目录')),
            (nuke.Boolean_Knob, 'use_wlf_write', utf8('使用 wlf_Write 替换 Write')),
            (nuke.Boolean_Knob, 'is_auto_frame_range', utf8('自动设置工程帧范围')),
        ]
        for i in self.knob_list:
            k = i[0](i[1], i[2])
            try:
                k.setValue(self.cfg.get(i[1]))
            except TypeError:
                pass
            self.addKnob(k)
        for i in ('seq_include', 'seq_exclude', 'use_wlf_write', 'is_auto_frame_range', 'override_project_directory'):
            self.knobs()[i].setFlag(nuke.STARTLINE)

    def knobChanged(self, knob):
        """Override for buttons."""

        if knob is self.knobs()['OK']:
            self.update_config()

    def update_config(self):
        """Write all setting to config.  """

        for i in self.knob_list:
            if i[1] in self.cfg:
                self.cfg[i[1]] = self.knobs()[i[1]].value()


class BatchPanel(nukescripts.PythonPanel):
    """Dialog UI of class BatchComp."""

    knob_list = [
        (nuke.File_Knob, 'input_dir', '输入文件夹'),
        (nuke.File_Knob, 'output_dir', '输出文件夹'),
        (nuke.Script_Knob, 'setting', '设置'),
    ]

    def __init__(self):
        nukescripts.PythonPanel.__init__(
            self, utf8('批量单帧工程转换'), 'com.wlf.batch_script_use_seq')
        self._shot_list = None
        self.cfg = Config().read()

        for i in self.knob_list:
            k = i[0](*iutf8(i[1:]))
            try:
                k.setValue(utf8(self.cfg.get(i[1])))
            except TypeError:
                pass
            self.addKnob(k)
        for i in ('input_dir', 'output_dir', 'setting'):
            self.knobs()[i].setFlag(nuke.STARTLINE)

    def knobChanged(self, knob):
        """Override for buttons."""

        name = knob.name()

        if name == 'OK':
            self.confirm()

        if name == 'setting':
            self.show_setting()

    @run_async
    @run_in_main_thread
    def show_setting(self):
        """Show comp setting.  """

        ConfigPanel().showModalDialog()

    def update_config(self):
        """Write all setting to config.  """

        self.cfg['input_dir'] = self.knobs()['input_dir'].value()
        self.cfg['output_dir'] = self.knobs()['output_dir'].value()

    def confirm(self):
        self.update_config()
        if not self.cfg['input_dir'] or not self.cfg['output_dir']:
            nuke.message(utf8("未填写输入或输出文件夹"))
            raise RuntimeError("cancel")
        batch.run(self.cfg['input_dir'], self.cfg['output_dir'])
