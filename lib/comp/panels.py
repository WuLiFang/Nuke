# -*- coding=UTF-8 -*-
"""Nuke panels for comp.  """

from __future__ import absolute_import, print_function, unicode_literals

import os
import webbrowser

import cast_unknown as cast
import nuke
import nukescripts  # pylint: disable=import-error
import psutil

from comp.batch import BatchComp
from comp.config import (IGNORE_EXISTED, MULTI_THREADING, BatchCompConfig,
                         CompConfig)
from wlf.decorators import run_async, run_in_main_thread
import cast_unknown as cast


class CompConfigPanel(nukescripts.PythonPanel):
    """UI of comp config.  """

    knob_list = [
        (nuke.File_Knob, 'mp', cast.binary('指定MP')),
        (nuke.File_Knob, 'mp_lut', cast.binary('MP LUT')),
        (nuke.Tab_Knob, 'parts', cast.binary('节点组开关')),
        (nuke.Boolean_Knob, 'precomp', cast.binary('预合成')),
        (nuke.Boolean_Knob, 'masks', cast.binary('预建常用mask')),
        (nuke.Boolean_Knob, 'colorcorrect', cast.binary('预建调色节点')),
        (nuke.Boolean_Knob, 'filters', cast.binary('预建滤镜节点')),
        (nuke.Boolean_Knob, 'zdefocus', cast.binary('预建ZDefocus')),
        (nuke.Boolean_Knob, 'depth', cast.binary('合并depth')),
        (nuke.Boolean_Knob, 'other', cast.binary('合并其他通道')),
        (nuke.Tab_Knob, 'filter', cast.binary('正则过滤')),
        (nuke.String_Knob, 'footage_pat', cast.binary('素材名')),
        (nuke.String_Knob, 'tag_pat', cast.binary('标签')),
        (nuke.Script_Knob, 'reset', cast.binary('重置')),
    ]

    def __init__(self):
        nukescripts.PythonPanel.__init__(
            self,
            cast.binary('自动合成设置'),
            b'com.wlf.comp',
        )
        self._shot_list = None
        self.cfg = CompConfig().read()

        for i in self.knob_list:
            k = i[0](i[1], i[2])
            try:
                k.setValue(self.cfg.get(i[1]))
            except TypeError:
                pass
            self.addKnob(k)
        for i in ('reset', 'precomp', 'masks', 'colorcorrect', 'filters', 'zdefocus',
                  'depth', 'other'):
            self.knobs()[i].setFlag(nuke.STARTLINE)

    def knobChanged(self, knob):
        """Overrride for buttons."""

        if knob is self.knobs()['OK']:
            self.update_config()
        elif knob is self.knobs()['reset']:
            self.reset()

    def reset(self):
        """Reset re pattern.  """

        for i in ('footage_pat', 'tag_pat'):
            knob = self.knobs()[i]
            knob.setValue(self.cfg.default.get(i))
            self.knobChanged(knob)

    def update_config(self):
        """Write all setting to config.  """

        for i in self.knob_list:
            if i[1] in self.cfg:
                self.cfg[i[1]] = self.knobs()[i[1]].value()


class BatchCompPanel(nukescripts.PythonPanel):
    """Dialog UI of class BatchComp."""

    knob_list = [
        (nuke.File_Knob, 'input_dir', '输入文件夹'),
        (nuke.File_Knob, 'output_dir', '输出文件夹'),
        (nuke.Boolean_Knob, 'exclude_existed', '排除已输出镜头'),
        (nuke.Script_Knob, 'setting', '合成设置'),
        (nuke.Text_Knob, '', ''),
        (nuke.String_Knob, 'txt_name', ''),
        (nuke.Script_Knob, 'generate_txt', '生成'),
        (nuke.Multiline_Eval_String_Knob, 'info', ''),
        (nuke.String_Knob, 'dir_pat', '文件夹正则'),
        (nuke.Script_Knob, 'reset', '重置'),
    ]

    def __init__(self):
        nukescripts.PythonPanel.__init__(
            self, cast.binary('批量合成'), b'com.wlf.batchcomp')
        self._shot_list = None
        self.cfg = BatchCompConfig().read()

        for i in self.knob_list:
            k = i[0](*(cast.binary(j) for j in i[1:]))
            try:
                k.setValue(cast.binary(self.cfg.get(i[1])))
            except TypeError:
                pass
            self.addKnob(k)
        for i in ('exclude_existed',):
            self.knobs()[i].setFlag(nuke.STARTLINE)
        self.knobs()['generate_txt'].setLabel(
            cast.binary('生成 {}.txt'.format(self.txt_name)))

    def __getattr__(self, name):
        return self.knobs()[name].value()

    def knobChanged(self, knob):
        """Override for buttons."""

        name = knob.name()

        if name == 'OK':
            self.batchcomp.start()
        elif name == 'reset':
            self.reset()
        elif name == 'generate_txt':
            self.generate_txt()
        elif name == 'setting':
            self.show_setting()
        elif name == 'txt_name':
            self.knobs()['generate_txt'].setLabel(
                '生成 {}.txt'.format(self.txt_name))
        elif name in self.knobs():
            self.cfg[name] = knob.value()

        self.update()

    @run_async
    @run_in_main_thread
    def show_setting(self):
        """Show comp setting.  """

        CompConfigPanel().showModalDialog()

    def generate_txt(self):
        """Generate txt contain shot list.  """

        shots = self.batchcomp.get_shot_list()
        path = os.path.join(self.output_dir, '{}.txt'.format(self.txt_name))
        line_width = max(len(i) for i in shots)
        if os.path.exists(cast.binary(path)) and not nuke.ask('文件已存在, 是否覆盖?'):
            return
        with open(cast.binary(path), 'w') as f:
            f.write('\n\n'.join('{: <{width}s}: '.format(i, width=line_width)
                                for i in shots))
        webbrowser.open(path)

    @property
    def txt_name(self):
        """Output txt name. """
        return cast.text(self.knobs()['txt_name'].value())

    @property
    def batchcomp(self):
        """Batch comp object related to current setting. """

        i_dir = self.input_dir
        o_dir = self.output_dir

        flags = 0
        if self.knobs()['exclude_existed'].value():
            flags |= IGNORE_EXISTED
        if psutil.virtual_memory().free > 16 * 1024 ** 3:
            flags |= MULTI_THREADING

        return BatchComp(i_dir, o_dir, flags=flags)

    def reset(self):
        """Reset re pattern.  """

        for i in ('dir_pat',):
            knob = self.knobs()[i]
            knob.setValue(cast.binary(self.cfg.default.get(i)))
            self.knobChanged(knob)

    def update(self):
        """Update ui info and button enabled."""

        def _info():
            _info = u'测试'
            self._shot_list = list(self.batchcomp.get_shot_list())
            if self._shot_list:
                _info = u'# 共{}个镜头\n'.format(len(self._shot_list))
                _info += u'\n'.join(self._shot_list)
            else:
                _info = u'找不到镜头'
            self.knobs()['info'].setValue(cast.binary(_info))

        def _button_enabled():
            _knobs = [
                'output_dir',
                'exclude_existed',
                'info',
                'OK',
            ]

            _isdir = os.path.isdir(self.cfg['input_dir'])
            if _isdir:
                for k in ['exclude_existed', 'info']:
                    self.knobs()[k].setEnabled(True)
                if self._shot_list:
                    for k in _knobs:
                        self.knobs()[k].setEnabled(True)
                else:
                    for k in set(_knobs) - set(['exclude_existed']):
                        self.knobs()[k].setEnabled(False)
            else:
                for k in _knobs:
                    self.knobs()[k].setEnabled(False)

        _info()
        _button_enabled()
