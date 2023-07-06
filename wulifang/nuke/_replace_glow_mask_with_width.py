# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang._util import cast_str, cast_text
from wulifang.nuke._util import (
    knob_of,
    create_node,
)


def replace():
    # type: () -> None
    """Use width channel on `Glow2` node, instead of mask."""

    nodes = nuke.allNodes(cast_str("Glow2"))
    result = [n for n in nodes if _replace_glow_mask(n)]

    if result:

        nuke.message(
            cast_str(
                "将 %s 个 Glow 节点的 mask 用 width channel 代替:\n%s"
                % (
                    len(result),
                    ",".join(cast_text(n.name()) for n in result),
                )
            )
        )
    else:
        nuke.message(cast_str("没有发现使用了 mask 的 Glow 节点"))


def _replace_glow_mask(
    n,  # type: nuke.Node
):

    mask_channel_mask_knob = knob_of(n, "maskChannelMask", nuke.Channel_Knob)
    mask_channel_input_knob = knob_of(n, "maskChannelInput", nuke.Channel_Knob)
    w_knob = knob_of(n, "W", nuke.Channel_Knob)
    mask_knob = mask_channel_mask_knob if n.input(1) else mask_channel_input_knob
    mask_channel = cast_text(mask_knob.value())

    if mask_channel == "none":
        return False

    copy_node = create_node(
        "Copy",
        "from0 %s\nto0 mask.a" % (mask_channel,),
        inputs=(n.input(0), n.input(1)),
    )
    copy_node.setXYpos(n.xpos(), n.ypos() - max(copy_node.screenHeight(), 32) - 10)
    width_channel = cast_text(knob_of(n, "W", nuke.Channel_Knob).value())
    if width_channel != "none":
        input0 = create_node(
            "ChannelMerge",
            "A mask.a\nB %s\noperation in" % (mask_channel,),
            inputs=(copy_node, copy_node),
        )
    else:
        input0 = copy_node

    n.setInput(0, input0)
    n.setInput(1, None)
    mask_channel_mask_knob.setValue(cast_str("none"))
    mask_channel_input_knob.setValue(cast_str("none"))
    w_knob.setValue(cast_str("mask.a"))

    return True
