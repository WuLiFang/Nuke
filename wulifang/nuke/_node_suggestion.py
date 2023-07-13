# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

import wulifang
import wulifang.nuke
from wulifang._util import (
    cast_text,
)


def _on_user_create():
    n = nuke.thisNode()
    class_ = cast_text(n.Class())
    if class_ in ("OFXcom.genarts.sapphire.stylize.s_halftone_v1",):
        wulifang.message.info("S_Halftone 节点性能不佳，建议用 Hatch 节点代替")
        return
    if class_ in ("OFXcom.genarts.sapphire.stylize.s_halftonecolor_v1",):
        wulifang.message.info("S_HalftoneColor 节点性能不佳，建议用 Hatch 节点代替")
        return
    if class_ in ("OFXcom.genarts.sapphire.stylize.s_vignette_v1",):
        wulifang.message.info("S_Vignette 节点会导致渲染卡顿，建议用 Vignette 节点代替")
        return
    if class_ in ("thersher"):
        wulifang.message.info("%s 节点来自第三方且效果不佳，建议用 Hatch 节点代替" % (class_,))
        return
    if class_ in ("RealHeatDist",):
        wulifang.message.info("%s 节点来自第三方，建议用 HeatDistort 节点代替" % (class_,))
        return
    if class_ in ("P_Matte", "P_Ramp"):
        wulifang.message.info("%s 节点来自第三方，建议用 PositionKeyer 节点代替" % (class_,))
        return
    if class_ in ("AutocomperArnold",):
        wulifang.message.info("%s 节点来自第三方，建议用 AOV 自动组装 (F1) 功能代替" % (class_,))
        return
    if class_ in ("Chromatic_Aberration",):
        wulifang.message.info("%s 节点来自第三方，建议用 Aberration 节点代替" % (class_,))
        return

    if class_ in ("Group",):
        name = cast_text(n.name())
        if name.startswith(
            "RealGlow",
        ):
            wulifang.message.info("RealGlow 节点来自第三方，建议用 SoftGlow 节点代替")
            return


def init_gui():
    wulifang.nuke.callback.on_user_create(_on_user_create)
