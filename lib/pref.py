# -*- coding=UTF-8 -*-
"""Custom nuke preference."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import logging

import nuke
import cast_unknown as cast
LOGGER = logging.getLogger('com.wlf.pref')


def set_knob_default():
    """Set nuke knob default when node create."""
    LOGGER.info(u'设置knob默认值')

    def _vectorblur2():
        nuke.knobDefault("VectorBlur2.uv", "motion")
        nuke.knobDefault("VectorBlur2.uv_offset", "0")
        nuke.knobDefault("VectorBlur2.scale", "1")
        nuke.knobDefault("VectorBlur2.soft_lines", "True")
        nuke.knobDefault("VectorBlur2.normalize", "True")

    def _root():
        nuke.knobDefault("Root.fps", "25")
        nuke.knobDefault("Root.format", "1920 1080 0 0 1920 1080 1 HD_1080")

    def _zdefocus2():
        nuke.knobDefault("ZDefocus2.blur_dof", "0")
        nuke.knobDefault("ZDefocus2.math", "depth")

    def _rolloffcontrast():
        nuke.knobDefault("RolloffContrast.contrast", "2")
        nuke.knobDefault("RolloffContrast.center", "0.001")
        nuke.knobDefault("RolloffContrast.soft_clip", "1")
        nuke.knobDefault("RolloffContrast.channels", "rgb")

    _root()
    _vectorblur2()
    _zdefocus2()
    _rolloffcontrast()
    nuke.knobDefault("LayerContactSheet.showLayerNames", "1")
    nuke.knobDefault("note_font", '微软雅黑')
    nuke.knobDefault("Switch.which", "1")
    nuke.knobDefault("Viewer.input_process", "False")
    nuke.knobDefault("SoftClip.conversion", "3")
    nuke.knobDefault("PositionToPoints.P_channel", "P")
    nuke.knobDefault('Roto.cliptype', 'no clip')
    nuke.knobDefault('RotoPaint.cliptype', 'no clip')
    nuke.knobDefault('Denoise2.type', 'Digital')

    k = cast.not_none(nuke.toNode(b'preferences'))[b'UIFontSize']
    if k.value() == 11:
        k.setValue(12)

    try:
        k = cast.not_none(nuke.toNode(b'preferences'))[
            b'LocalizationPauseOnProjectLoad']
        k.setValue(True)
    except NameError:
        LOGGER.debug(
            'Can not set localization preference, maybe using low version.')

    nuke.untitled = '未命名'


def add_preferences():
    """Add a prefrences panel."""
    LOGGER.info(u'添加首选项')
    pref = nuke.toNode(b'preferences')
    k = nuke.Tab_Knob(b'wlf_tab',  cast.binary('吾立方'))
    pref.addKnob(k)

    def _remove_old():
        for k in [b'wlf_lock_connection', b'wlf_tab']:
            try:
                pref.removeKnob(pref[k])
            except NameError:
                pass

    def _add_knob(k):
        _knob_tcl_name = 'preferences.{}'.format(k.name())
        if nuke.exists(cast.binary(_knob_tcl_name)):
            k.setValue(pref[k.name()].value())
            pref.removeKnob(pref[k.name()])
        k.setFlag(nuke.ALWAYS_SAVE)
        pref.addKnob(k)

    knob_list = [
        (nuke.String_Knob, ('wlf_artist', '制作人信息')),
        (nuke.Boolean_Knob, ('wlf_gizmo_to_group', '创建Gizmo时尝试转换为Group')),
        (nuke.Boolean_Knob, ('wlf_eval_proj_dir', '读取时工程目录自动转换为绝对路径', True)),
        (nuke.Text_Knob, ('wlf_on_script_save', '保存时')),
        (nuke.Boolean_Knob, ('wlf_autoplace', '自动摆放节点')),
        (nuke.Enumeration_Knob,
         ('wlf_autoplace_type', '风格', ['竖式', '横式(Nuke)'])),
        (nuke.Boolean_Knob, ('wlf_lock_connections', '锁定节点连接')),
        (nuke.Boolean_Knob, ('wlf_enable_node', '启用被标记为稍后启用的节点', True)),
        (nuke.Boolean_Knob, ('wlf_jump_frame', '跳至_Write节点指定的帧', True)),
        (nuke.Text_Knob, ('wlf_on_script_close', '保存并退出时')),
        (nuke.Boolean_Knob, ('wlf_render_jpg', '渲染_Write节点单帧', True)),
        (nuke.Boolean_Knob, ('wlf_send_to_dir', '发送至渲染文件夹')),
        (nuke.File_Knob, ('wlf_render_dir', '')),
    ]

    for i in knob_list:
        k = i[0](*i[1])
        if i[1][0] in ('wlf_render_dir', 'wlf_autoplace_type'):
            k.clearFlag(nuke.STARTLINE)
        else:
            k.setFlag(nuke.STARTLINE)
        _add_knob(k)

    _remove_old()


def setup():
    """Setup preferences.   """

    set_knob_default()
    add_preferences()
