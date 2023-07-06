# -*- coding=UTF-8 -*-
"""Custom nuke preference."""
from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional

import nuke
import os
import wulifang
from wulifang.vendor.Qt.QtCore import QTimer
from wulifang._util import cast_str, assert_not_none, assert_isinstance


def init():
    wulifang.message.debug("设置knob默认值")

    nuke.knobDefault(cast_str("VectorBlur2.uv"), cast_str("motion"))
    nuke.knobDefault(cast_str("VectorBlur2.uv_offset"), cast_str("0"))
    nuke.knobDefault(cast_str("VectorBlur2.scale"), cast_str("1"))
    nuke.knobDefault(cast_str("VectorBlur2.soft_lines"), cast_str("True"))
    nuke.knobDefault(cast_str("VectorBlur2.normalize"), cast_str("True"))

    nuke.knobDefault(cast_str("Root.fps"), cast_str("25"))
    nuke.knobDefault(
        cast_str("Root.format"), cast_str("1920 1080 0 0 1920 1080 1 HD_1080")
    )

    nuke.knobDefault(cast_str("ZDefocus2.blur_dof"), cast_str("0"))
    nuke.knobDefault(cast_str("ZDefocus2.math"), cast_str("depth"))

    nuke.knobDefault(cast_str("RolloffContrast.contrast"), cast_str("2"))
    nuke.knobDefault(cast_str("RolloffContrast.center"), cast_str("0.001"))
    nuke.knobDefault(cast_str("RolloffContrast.soft_clip"), cast_str("1"))
    nuke.knobDefault(cast_str("RolloffContrast.channels"), cast_str("rgb"))

    nuke.knobDefault(cast_str("LayerContactSheet.showLayerNames"), cast_str("1"))
    nuke.knobDefault(cast_str("note_font"), cast_str("微软雅黑"))
    nuke.knobDefault(cast_str("Switch.which"), cast_str("1"))
    nuke.knobDefault(cast_str("Viewer.input_process"), cast_str("False"))
    nuke.knobDefault(cast_str("SoftClip.conversion"), cast_str("3"))
    nuke.knobDefault(cast_str("PositionToPoints.P_channel"), cast_str("P"))
    nuke.knobDefault(cast_str("Roto.cliptype"), cast_str("no clip"))
    nuke.knobDefault(cast_str("RotoPaint.cliptype"), cast_str("no clip"))
    nuke.knobDefault(cast_str("Denoise2.type"), cast_str("Digital"))

    nuke.knobDefault(cast_str("preferences.UIFontSize"), cast_str("12"))
    nuke.knobDefault(
        cast_str("preferences.LocalizationPauseOnProjectLoad"), cast_str("True")
    )
    nuke.knobDefault(
        cast_str("preferences.wlf_artist"),
        cast_str(
            "%s@%s"
            % (
                os.getenv("USERNAME") or "anonymous",
                os.getenv("COMPUTERNAME") or "localhost",
            )
        ),
    )
    nuke.untitled = cast_str("未命名")


def _init_gui():
    wulifang.message.debug("添加首选项")
    pref = assert_not_none(nuke.toNode(cast_str("preferences")))

    def remove(name):
        # type: (Text) -> None
        try:
            pref.removeKnob(pref[cast_str(name)])
        except NameError:
            pass

    def add(k, inline=False):
        k = assert_isinstance(k, nuke.Knob)
        name = k.name()
        if name:
            tcl_name = "preferences.{}".format(k.name())
            if nuke.exists(cast_str(tcl_name)):
                k.setValue(pref[k.name()].value())
                pref.removeKnob(pref[k.name()])
        k.setFlag(nuke.ALWAYS_SAVE)
        if inline:
            k.clearFlag(nuke.STARTLINE)
        else:
            k.setFlag(nuke.STARTLINE)
        pref.addKnob(k)

    remove("wlf_lock_connection")
    remove("wlf_create_csheet")
    add(nuke.Tab_Knob(cast_str("wlf_tab"), cast_str("吾立方")))
    add(
        nuke.String_Knob(
            cast_str("wlf_artist"),
            cast_str("制作人信息"),
        )
    )
    add(nuke.Boolean_Knob(cast_str("wlf_eval_proj_dir"), cast_str("读取时工程目录自动转换为绝对路径")))
    add(
        nuke.Text_Knob(
            cast_str("wlf_on_script_save"),
            cast_str("保存时"),
        )
    )
    add(
        nuke.Boolean_Knob(
            cast_str("wlf_autoplace"),
            cast_str("自动摆放节点"),
        ),
        True,
    )
    add(
        nuke.Enumeration_Knob(
            cast_str("wlf_autoplace_type"),
            cast_str("风格"),
            [
                cast_str("竖式"),
                cast_str("横式(Nuke)"),
            ],
        ),
        True,
    )
    add(
        nuke.Boolean_Knob(
            cast_str("wlf_lock_connections"),
            cast_str("锁定节点连接"),
        )
    )
    add(
        nuke.Boolean_Knob(
            cast_str("wlf_enable_node"),
            cast_str("启用被标记为稍后启用的节点"),
            True,
        )
    )
    add(
        nuke.Boolean_Knob(
            cast_str("wlf_jump_frame"),
            cast_str("跳至_Write节点指定的帧"),
            True,
        )
    )
    add(
        nuke.Text_Knob(
            cast_str("wlf_on_script_close"),
            cast_str("保存并退出时"),
        )
    )
    add(
        nuke.Boolean_Knob(
            cast_str("wlf_render_jpg"),
            cast_str("渲染_Write节点单帧"),
            True,
        )
    )
    add(
        nuke.Boolean_Knob(
            cast_str("wlf_send_to_dir"),
            cast_str("发送至渲染文件夹"),
        )
    )
    add(
        nuke.File_Knob(
            cast_str("wlf_render_dir"),
            cast_str(""),
        ),
        True,
    )

    # remove empty tab
    tab = None  # type: Optional[nuke.Tab_Knob]
    count = 0
    for k in pref.allKnobs():
        if isinstance(k, nuke.Tab_Knob):
            if tab and count == 0:
                pref.removeKnob(tab)
            tab = k
            count = 0
        else:
            count += 1
    if tab and count == 0:
        pref.removeKnob(tab)

    if nuke.NUKE_VERSION_MAJOR >= 12:
        # XXX: last tab not visible in nuke12
        add(nuke.Tab_Knob(cast_str("")))


def init_gui():
    # wait pref node been created
    QTimer.singleShot(0, _init_gui)
