# -*- coding=UTF-8 -*-
"""Custom nuke preference."""
from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional

import nuke
import os
import wulifang
import wulifang.vendor.cast_unknown as cast
from wulifang.vendor.Qt.QtCore import QTimer
from wulifang._util import cast_binary


def init():
    wulifang.message.debug("设置knob默认值")

    nuke.knobDefault(b"VectorBlur2.uv", b"motion")
    nuke.knobDefault(b"VectorBlur2.uv_offset", b"0")
    nuke.knobDefault(b"VectorBlur2.scale", b"1")
    nuke.knobDefault(b"VectorBlur2.soft_lines", b"True")
    nuke.knobDefault(b"VectorBlur2.normalize", b"True")

    nuke.knobDefault(b"Root.fps", b"25")
    nuke.knobDefault(b"Root.format", b"1920 1080 0 0 1920 1080 1 HD_1080")

    nuke.knobDefault(b"ZDefocus2.blur_dof", b"0")
    nuke.knobDefault(b"ZDefocus2.math", b"depth")

    nuke.knobDefault(b"RolloffContrast.contrast", b"2")
    nuke.knobDefault(b"RolloffContrast.center", b"0.001")
    nuke.knobDefault(b"RolloffContrast.soft_clip", b"1")
    nuke.knobDefault(b"RolloffContrast.channels", b"rgb")

    nuke.knobDefault(b"LayerContactSheet.showLayerNames", b"1")
    nuke.knobDefault(b"note_font", cast.binary("微软雅黑"))
    nuke.knobDefault(b"Switch.which", b"1")
    nuke.knobDefault(b"Viewer.input_process", b"False")
    nuke.knobDefault(b"SoftClip.conversion", b"3")
    nuke.knobDefault(b"PositionToPoints.P_channel", b"P")
    nuke.knobDefault(b"Roto.cliptype", b"no clip")
    nuke.knobDefault(b"RotoPaint.cliptype", b"no clip")
    nuke.knobDefault(b"Denoise2.type", b"Digital")

    nuke.knobDefault(b"preferences.UIFontSize", b"12")
    nuke.knobDefault(b"preferences.LocalizationPauseOnProjectLoad", b"True")
    nuke.knobDefault(
        b"preferences.wlf_artist",
        (
            "%s@%s"
            % (
                os.getenv("USERNAME") or "anonymous",
                os.getenv("COMPUTERNAME") or "localhost",
            )
        ).encode("utf-8"),
    )
    nuke.untitled = cast.binary("未命名")


def _init_gui():
    wulifang.message.debug("添加首选项")
    pref = cast.not_none(nuke.toNode(b"preferences"))

    def remove(name):
        # type: (Text) -> None
        try:
            pref.removeKnob(pref[cast_binary(name)])
        except NameError:
            pass

    def add(k, inline=False):
        k = cast.instance(k, nuke.Knob)
        name = k.name()
        if name:
            tcl_name = "preferences.{}".format(k.name())
            if nuke.exists(cast.binary(tcl_name)):
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
    add(nuke.Tab_Knob(b"wlf_tab", "吾立方".encode("utf-8")))
    add(
        nuke.String_Knob(
            b"wlf_artist",
            cast.binary("制作人信息"),
        )
    )
    add(
        nuke.Boolean_Knob(b"wlf_gizmo_to_group", cast.binary("创建Gizmo时尝试转换为Group")),
    )
    add(nuke.Boolean_Knob(b"wlf_eval_proj_dir", cast.binary("读取时工程目录自动转换为绝对路径")))
    add(
        nuke.Text_Knob(
            b"wlf_on_script_save",
            cast.binary("保存时"),
        )
    )
    add(
        nuke.Boolean_Knob(
            b"wlf_autoplace",
            cast.binary("自动摆放节点"),
        ),
        True,
    )
    add(
        nuke.Enumeration_Knob(
            b"wlf_autoplace_type",
            cast.binary("风格"),
            [
                cast.binary("竖式"),
                cast.binary("横式(Nuke)"),
            ],
        ),
        True,
    )
    add(
        nuke.Boolean_Knob(
            b"wlf_lock_connections",
            cast.binary("锁定节点连接"),
        )
    )
    add(
        nuke.Boolean_Knob(
            b"wlf_enable_node",
            cast.binary("启用被标记为稍后启用的节点"),
            True,
        )
    )
    add(
        nuke.Boolean_Knob(
            b"wlf_jump_frame",
            cast.binary("跳至_Write节点指定的帧"),
            True,
        )
    )
    add(
        nuke.Text_Knob(
            b"wlf_on_script_close",
            cast.binary("保存并退出时"),
        )
    )
    add(
        nuke.Boolean_Knob(
            b"wlf_render_jpg",
            cast.binary("渲染_Write节点单帧"),
            True,
        )
    )
    add(
        nuke.Boolean_Knob(
            b"wlf_send_to_dir",
            cast.binary("发送至渲染文件夹"),
        )
    )
    add(
        nuke.File_Knob(
            b"wlf_render_dir",
            cast.binary(""),
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
        add(nuke.Tab_Knob(b""))


def init_gui():
    # wait pref node been created
    QTimer.singleShot(0, _init_gui)
