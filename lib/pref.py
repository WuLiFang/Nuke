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
        _ = nuke.knobDefault(b"VectorBlur2.uv", b"motion")
        _ = nuke.knobDefault(b"VectorBlur2.uv_offset", b"0")
        _ = nuke.knobDefault(b"VectorBlur2.scale", b"1")
        _ = nuke.knobDefault(b"VectorBlur2.soft_lines", b"True")
        _ = nuke.knobDefault(b"VectorBlur2.normalize", b"True")

    def _root():
        _ = nuke.knobDefault(b"Root.fps", b"25")
        _ = nuke.knobDefault(
            b"Root.format", b"1920 1080 0 0 1920 1080 1 HD_1080")

    def _zdefocus2():
        _ = nuke.knobDefault(b"ZDefocus2.blur_dof", b"0")
        _ = nuke.knobDefault(b"ZDefocus2.math", b"depth")

    def _rolloffcontrast():
        _ = nuke.knobDefault(b"RolloffContrast.contrast", b"2")
        _ = nuke.knobDefault(b"RolloffContrast.center", b"0.001")
        _ = nuke.knobDefault(b"RolloffContrast.soft_clip", b"1")
        _ = nuke.knobDefault(b"RolloffContrast.channels", b"rgb")

    _root()
    _vectorblur2()
    _zdefocus2()
    _rolloffcontrast()
    _ = nuke.knobDefault(b"LayerContactSheet.showLayerNames", b"1")
    _ = nuke.knobDefault(b"note_font", cast.binary('微软雅黑'))
    _ = nuke.knobDefault(b"Switch.which", b"1")
    _ = nuke.knobDefault(b"Viewer.input_process", b"False")
    _ = nuke.knobDefault(b"SoftClip.conversion", b"3")
    _ = nuke.knobDefault(b"PositionToPoints.P_channel", b"P")
    _ = nuke.knobDefault(b'Roto.cliptype', b'no clip')
    _ = nuke.knobDefault(b'RotoPaint.cliptype', b'no clip')
    _ = nuke.knobDefault(b'Denoise2.type', b'Digital')

    k = cast.not_none(nuke.toNode(b'preferences'))[b'UIFontSize']
    if k.value() == 11:
        _ = k.setValue(12)

    try:
        k = cast.not_none(nuke.toNode(b'preferences'))[
            b'LocalizationPauseOnProjectLoad']
        _ = k.setValue(True)
    except NameError:
        LOGGER.debug(
            'Can not set localization preference, maybe using low version.')

    nuke.untitled = cast.binary('未命名')


def add_preferences():
    """Add a prefrences panel."""
    LOGGER.info(u'添加首选项')
    pref = cast.not_none(nuke.toNode(b'preferences'))
    k = nuke.Tab_Knob(b'wlf_tab',  cast.binary('吾立方'))
    pref.addKnob(k)

    def _remove_old():
        for k in [b'wlf_lock_connection', b'wlf_tab']:
            try:
                pref.removeKnob(pref[k])
            except NameError:
                pass

    def _add_knob(k, inline=False):
        k = cast.instance(k, nuke.Knob)
        _knob_tcl_name = 'preferences.{}'.format(k.name())
        if nuke.exists(cast.binary(_knob_tcl_name)):
            _ = k.setValue(pref[k.name()].value())
            pref.removeKnob(pref[k.name()])
        k.setFlag(nuke.ALWAYS_SAVE)
        if inline:
            k.clearFlag(nuke.STARTLINE)
        else:
            k.setFlag(nuke.STARTLINE)
        pref.addKnob(k)

    _add_knob(nuke.String_Knob(
        b'wlf_artist',
        cast.binary('制作人信息'),
    ))
    _add_knob(nuke.Boolean_Knob(
        b'wlf_gizmo_to_group',
        cast.binary('创建Gizmo时尝试转换为Group')),
    )
    _add_knob(nuke.Boolean_Knob(
        b'wlf_eval_proj_dir',
        cast.binary('读取时工程目录自动转换为绝对路径')
    ), True)
    _add_knob(nuke.Text_Knob(
        b'wlf_on_script_save',
        cast.binary('保存时'),
    )),
    _add_knob(nuke.Boolean_Knob(
        b'wlf_autoplace',
        cast.binary('自动摆放节点'),
    ), True)
    _add_knob(nuke.Enumeration_Knob(
        b'wlf_autoplace_type',
        cast.binary('风格'),
        [
            cast.binary('竖式'),
            cast.binary('横式(Nuke)'),
        ],
    ))
    _add_knob(nuke.Boolean_Knob(
        b'wlf_lock_connections',
        cast.binary('锁定节点连接'),
    ))
    _add_knob(nuke.Boolean_Knob(
        b'wlf_enable_node',
        cast.binary('启用被标记为稍后启用的节点'),
        True,
    ))
    _add_knob(nuke.Boolean_Knob(
        b'wlf_jump_frame',
        cast.binary('跳至_Write节点指定的帧'),
        True,
    ))
    _add_knob(nuke.Text_Knob(
        b'wlf_on_script_close',
        cast.binary('保存并退出时'),
    ))
    _add_knob(nuke.Boolean_Knob(
        b'wlf_render_jpg',
        cast.binary('渲染_Write节点单帧'),
        True,
    ))
    _add_knob(nuke.Boolean_Knob(
        b'wlf_send_to_dir',
        cast.binary('发送至渲染文件夹'),
    ))
    _add_knob(nuke.File_Knob(
        b'wlf_render_dir',
        cast.binary(''),
    ), True)

    _remove_old()


def setup():
    """Setup preferences.   """

    set_knob_default()
    add_preferences()
