# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang._util import (
    cast_str,
    cast_int,
)
from wulifang.nuke._util import (
    undoable,
    knob_of,
)


def _create_frame(target, source, frame, direction):
    # type: (nuke.Node, nuke.Node, int, int) -> ...
    base_frame = frame - direction
    rgba = nuke.nodes.FrameHold(
        first_frame=base_frame,
        inputs=[target],
    )

    motion_current = nuke.nodes.FrameHold(first_frame=frame, inputs=[source])
    # backward: current frame motion + base frame rgba.
    motion = motion_current
    if direction > 0:
        # forward: base frame motion + base frame rgba.
        motion = nuke.nodes.FrameHold(
            first_frame=base_frame,
            inputs=[source],
        )

    copy = nuke.nodes.Merge2(
        operation="copy",
        Achannels="motion",
        Bchannels="motion",
        rangeinput="All",
        output="motion",
        inputs=[rgba, motion],
    )
    distort = nuke.nodes.IDistort(
        channels="rgba", uv="motion", uv_scale=-direction, inputs=[copy]
    )
    mask = nuke.nodes.Merge2(
        operation="mask",
        bbox="intersection",
        inputs=[distort, motion_current],
        disable="{{parent.disable_motion_mask}}",
    )
    cache = nuke.nodes.DiskCache(channels="rgba", inputs=[mask])
    switch = nuke.nodes.Switch(
        which="{{{{x=={}}}}}".format(frame),
        inputs=[target, cache],
        label=cast_str("frame {}".format(frame)),
    )
    return switch


@undoable("运动扭曲")
def create(base_frame, frame_gte, frame_lte):
    # type: (int, int, int) -> nuke.Group
    """Create a motion distort group node for given frame range,

    Args:
        base_frame (int): Frame to use as base frame.
        frame_gte (int): Frame greater than or equal.
        frame_lte (int): Frame less than or equal.

    Return:
        nuke.Node: Group node.
    """
    group = nuke.nodes.Group(tile_color=0xA57AAAFF)
    assert isinstance(group, nuke.Group)
    group.setName(cast_str("MotionDistort1"))
    group.addKnob(nuke.Tab_Knob(cast_str(""), cast_str("MotionDistort v0.2.2")))
    group.addKnob(nuke.Boolean_Knob(cast_str("disable_motion_mask")))
    group.addKnob(nuke.EndTabGroup_Knob(cast_str("")))
    with group:
        input_ = nuke.nodes.Input(name=cast_str("Input"))
        input_motion = nuke.nodes.Input(name=cast_str("motion"))
        last = input_
        # forward
        for frame in range(base_frame + 1, frame_lte + 1, 1):
            last = _create_frame(last, input_motion, frame, 1)
        # backward
        for frame in range(base_frame - 1, frame_gte - 1, -1):
            last = _create_frame(last, input_motion, frame, -1)
        nuke.nodes.Output(inputs=[last])
    return group


def dialog():
    """GUI dialog for `create_motion_distort`

    Returns:
        type.Optional[nuke.node.TimeWarp]: created node
    """

    key_start = cast_str("起始帧")
    key_end = cast_str("结束帧")
    key_base = cast_str("基准帧")

    panel = nuke.Panel(cast_str("创建运动扭曲"))
    panel.addExpressionInput(key_base, cast_str(nuke.frame()))
    panel.addExpressionInput(key_start, nuke.value(cast_str("root.first_frame")))
    panel.addExpressionInput(key_end, nuke.value(cast_str("root.last_frame")))
    if not panel.show():
        return
    base = cast_int(panel.value(key_base))
    start = cast_int(panel.value(key_start))
    end = cast_int(panel.value(key_end))
    group = create(base, start, end)
    knob_of(group, "label", nuke.String_Knob).setValue(
        cast_str("{}({}-{})".format(base, start, end))
    )
    for i, n in enumerate(nuke.selectedNodes()[:2]):
        group.setInput(i, n)
