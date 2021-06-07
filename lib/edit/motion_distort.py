# -*- coding=UTF-8 -*-
"""Create distorted images for selected frame range based on motion data.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke
from six.moves import range
import cast_unknown as cast

import nuketools


def _create_motion_distort_frame(target, source, frame, direction):
    assert isinstance(target, nuke.Node)
    assert isinstance(source, nuke.Node)
    assert isinstance(frame, int)
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
        label=cast.binary("frame {}".format(frame)),
    )
    return switch


@nuketools.undoable_func("运动扭曲")
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
    group = nuke.nodes.Group(tile_color=0xA57AAAFF)
    assert isinstance(group, nuke.Group)
    group.setName(b"MotionDistort1")
    group.addKnob(nuke.Tab_Knob(b"", b"MotionDistort v0.2.2"))
    group.addKnob(nuke.Boolean_Knob(b"disable_motion_mask"))
    group.addKnob(nuke.EndTabGroup_Knob(b""))
    with group:
        input_ = nuke.nodes.Input(name=b"Input")
        input_motion = nuke.nodes.Input(name=b"motion")
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
        return cast.binary(
            {
                "start": "起始帧",
                "end": "结束帧",
                "base": "基准帧",
            }.get(key, key)
        )

    panel = nuke.Panel("创建运动扭曲".encode("utf8"))
    _ = panel.addExpressionInput(_tr("base"), cast.binary(nuke.frame()))
    _ = panel.addExpressionInput(_tr("start"), nuke.value(b"root.first_frame"))
    _ = panel.addExpressionInput(_tr("end"), nuke.value(b"root.last_frame"))
    if not panel.show():
        return
    base = int(cast.not_none(panel.value(_tr("base"))))
    start = int(cast.not_none(panel.value(_tr("start"))))
    end = int(cast.not_none(panel.value(_tr("end"))))
    group = create_motion_distrot(base, start, end)
    group[b"label"].setValue("{}({}-{})".format(base, start, end))
    for i, n in enumerate(nuke.selectedNodes()[:2]):
        _ = group.setInput(i, n)
