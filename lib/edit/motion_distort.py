# -*- coding=UTF-8 -*-
"""Create distorted images for selected frame range based on motion data.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke
from six.moves import range

import nuketools
from nuketools import utf8 as _
from orgnize import autoplace


def _create_motion_distort_frame(target, source, frame, direction):
    assert isinstance(target, nuke.Node)
    assert isinstance(source, nuke.Node)
    assert isinstance(frame, int)
    base_frame = frame-direction
    rgba = nuke.nodes.FrameHold(
        first_frame=base_frame,
        inputs=[target],
    )

    motion_current = nuke.nodes.FrameHold(
        first_frame=frame,
        inputs=[source]
    )
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
        channels="rgba",
        uv="motion",
        uv_scale=-direction,
        inputs=[copy]
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
        label="frame {}".format(frame)
    )
    return switch


@nuketools.undoable_func('运动扭曲')
def create_motion_distrot(base_frame, frame_gte, frame_lte):
    """Create a motion distort group node for given frame range,

    Args:
        base_frame (int): Frame to use as base frame.
        frame_gte (int): Frame greater than or equal.
        frame_lte (int): Frame less than or equal.

    Return:
        nuke.Node: Group node.
    """
    assert isinstance(frame_gte, int)
    assert isinstance(frame_lte, int)
    group = nuke.nodes.Group(tile_color="0xa57aaaff")
    group.setName("MotionDistort1")
    group.addKnob(nuke.Tab_Knob("", "MotionDistort v0.2.2"))
    group.addKnob(nuke.Boolean_Knob("disable_motion_mask"))
    group.addKnob(nuke.EndTabGroup_Knob(""))
    with group:
        input_ = nuke.nodes.Input(name="Input")
        input_motion = nuke.nodes.Input(name="motion")
        last = input_
        # forward
        for frame in range(base_frame + 1, frame_lte + 1, 1):
            last = _create_motion_distort_frame(last, input_motion, frame, 1)
        # backward
        for frame in range(base_frame - 1, frame_gte - 1, -1):
            last = _create_motion_distort_frame(last, input_motion, frame, -1)
        output = nuke.nodes.Output(inputs=[last])
    return group


def show_motion_distort_dialog():
    """GUI dialog for `create_motion_distort`

    Returns:
        type.Optional[nuke.node.TimeWarp]: created node
    """

    def _tr(key):
        return _({
            'start': '起始帧',
            'end': '结束帧',
            'base': '基准帧',
        }.get(key, key))

    panel = nuke.Panel("创建运动扭曲".encode("utf8"))
    panel.addExpressionInput(_tr('base'), nuke.frame())
    panel.addExpressionInput(_tr('start'), nuke.numvalue("root.first_frame"))
    panel.addExpressionInput(_tr('end'), nuke.numvalue("root.last_frame"))
    if not panel.show():
        return
    base = int(panel.value(_tr('base')))
    start = int(panel.value(_tr('start')))
    end = int(panel.value(_tr('end')))
    group = create_motion_distrot(base, start, end)
    group["label"].setValue("{}({}-{})".format(base, start, end))
    for i, n in enumerate(nuke.selectedNodes()[:2]):
        group.setInput(i, n)
