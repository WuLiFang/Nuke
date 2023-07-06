# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke
from nuke.curvelib import CVec3
import nuke.curveknob
import nuke.curvelib

from wulifang._util import (
    cast_str,
    cast_text,
    cast_int,
)
from wulifang.nuke._util import (
    undoable,
    Progress,
    knob_of,
    RotoKnob,
    iter_rotopaint_anim_control_point,
    iter_deep_rotopaint_shape,
    RelativeRotopaintAnimControlPoint,
    RotopaintLifeTimeType,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Union, Callable, Iterator, Iterable


def _is_point_single_key(point):
    # type: (nuke.curveknob.ShapeControlPoint) -> bool
    return all(
        len(p.getControlPointKeyTimes()) == 1
        for p in iter_rotopaint_anim_control_point(point)
    )


def _is_shape_single_key(shape):
    # type: (nuke.curveknob.Shape) -> bool
    return all(_is_point_single_key(p) for p in shape)


def _motion_distort_rotopaint_anim_point_frame(motion, point, frame, direction):
    # type: (nuke.Node, Union[nuke.curvelib.AnimControlPoint,RelativeRotopaintAnimControlPoint], int, int) -> Callable[[], None]
    base_frame = frame - direction
    motion_frame = base_frame
    if direction < 0:
        motion_frame -= 1
    base_pos = point.getPosition(base_frame)
    offset = CVec3(
        motion.sample(
            cast_str("forward.u"),
            base_pos.x,
            base_pos.y,
            frame=motion_frame,
        ),
        motion.sample(
            cast_str("forward.v"),
            base_pos.x,
            base_pos.y,
            frame=motion_frame,
        ),
    )
    computed_pos = base_pos + offset * direction

    def _job():
        point.addPositionKey(frame, computed_pos)

    return _job


def _motion_distort_rotopaint_shape_point_frame(motion, point, frame, direction):
    # type: (nuke.Node, nuke.curveknob.ShapeControlPoint, int, int) -> None
    # we should change center after sample finished.
    deferred_jobs = []  # type: list[Callable[[],None]]
    for i in iter_rotopaint_anim_control_point(point):
        job = _motion_distort_rotopaint_anim_point_frame(
            motion,
            i,
            frame,
            direction,
        )
        deferred_jobs.append(job)

    for i in deferred_jobs:
        i()


def _remove_shape_point_position_key(point, frame):
    # type: (nuke.curveknob.ShapeControlPoint, int) -> None
    for i in iter_rotopaint_anim_control_point(point):
        i.removePositionKey(frame)


def _motion_distort_rotopaint_shape_point(
    motion, point, base_frame, frame_gte, frame_lte, interval
):
    # type: (nuke.Node, nuke.curveknob.ShapeControlPoint, int, int, int, int) -> None
    # base
    _motion_distort_rotopaint_shape_point_frame(motion, point, base_frame, 0)
    # backward
    for i in range(base_frame - 1, frame_gte - 1, -1):
        _motion_distort_rotopaint_shape_point_frame(motion, point, i, -1)
    # forward
    for i in range(base_frame + 1, frame_lte + 1):
        _motion_distort_rotopaint_shape_point_frame(motion, point, i, 1)
    # interval
    for i in range(frame_gte, frame_lte + 1):
        if (i - base_frame) % interval != 0:
            _remove_shape_point_position_key(point, i)


def _motion_distort_rotopaint_shape(
    motion, shape, base_frame, frame_gte, frame_lte, interval
):
    # type: (nuke.Node, nuke.curveknob.Shape, int, int, int, int) -> None
    for i in shape:
        _motion_distort_rotopaint_shape_point(
            motion, i, base_frame, frame_gte, frame_lte, interval
        )


_GENERATED_SHAPE_SUFFIX = ".MotionDistort"


def _iter_matched_shape(layer):
    # type: (nuke.curveknob.Layer) -> Iterator[nuke.curveknob.Shape]
    for i in iter_deep_rotopaint_shape(layer):
        attrs = i.getAttributes()
        visible_curve = attrs.getCurve(attrs.kVisibleAttribute)
        if not visible_curve.constantValue or visible_curve.getNumberOfKeys() > 0:
            continue
        lifetime_type = attrs.getCurve(attrs.kLifeTimeTypeAttribute).constantValue
        if lifetime_type != RotopaintLifeTimeType:
            continue
        if not (
            cast_text(i.name).endswith(_GENERATED_SHAPE_SUFFIX)
            or _is_shape_single_key(i)
        ):
            continue
        yield i


@undoable("RotoPaint 运动扭曲")
def create(
    rotopaint,
    base_frame,
    frame_gte,
    frame_lte,
    interval,
):
    # type: (nuke.Node, int, int, int, int) -> None
    """Create motion distort shape for condition matched shape.

    Args:
        rotopaint (nuke.nodes.RotoPaint): RotoPaint node that contains
            motion data and shape.
        base_frame (int): Base frame to motion from.
        frame_gte (int): Frame range start.
        frame_lte (int): Frame range end.
        interval (int): Keep keyframe every n frame
            for generated shape, remove others.
    """
    assert rotopaint.Class() == "RotoPaint", "should be rotopaint, got {}".format(
        rotopaint.Class()
    )
    k = knob_of(rotopaint, "curves", RotoKnob)
    layer = k.rootLayer
    existed_shape = {cast_text(i.name): i for i in iter_deep_rotopaint_shape(layer)}
    with Progress(cast_text(rotopaint.name())) as p:
        for i in _iter_matched_shape(layer):
            p.increase()
            name = cast_text(i.name)
            p.set_message(name)
            is_generated = name.endswith(_GENERATED_SHAPE_SUFFIX)
            if not is_generated:
                name += _GENERATED_SHAPE_SUFFIX
            v = existed_shape.get(name) or i.clone()
            v.name = cast_str(name)

            if not is_generated:
                attrs = i.getAttributes()
                attrs.getCurve(attrs.kVisibleAttribute).constantValue = False
                i.locked = True

            _motion_distort_rotopaint_shape(
                rotopaint,
                v,
                base_frame,
                frame_gte,
                frame_lte,
                interval,
            )


def dialog(_nodes):
    # type: (Iterable[nuke.Node]) -> None
    """Show GUI dialog for `create_rotopaint_motion_distort`."""

    # Node.sample need a transformed position when using proxy
    knob_of(nuke.root(), "proxy", nuke.Boolean_Knob).setValue(False)

    key_start = cast_str("起始帧")
    key_end = cast_str("结束帧")
    key_base = cast_str("基准帧")
    key_interval = cast_str("间隔")

    panel = nuke.Panel(cast_str("创建 RotoPaint 运动扭曲"))
    panel.addExpressionInput(key_base, cast_str(nuke.frame()))
    panel.addExpressionInput(
        key_start, cast_str(nuke.numvalue(cast_str("root.first_frame")))
    )
    panel.addExpressionInput(
        key_end, cast_str(nuke.numvalue(cast_str("root.last_frame")))
    )
    panel.addExpressionInput(key_interval, cast_str("1"))
    if not panel.show():
        return
    base = cast_int(panel.value(key_base))
    start = cast_int(panel.value(key_start))
    end = cast_int(panel.value(key_end))
    interval = cast_int(panel.value(key_interval))

    with Progress("RotoPaint 运动扭曲") as p:
        for n in _nodes:
            p.increase()
            if cast_text(n.Class()) != "RotoPaint": 
                continue
            p.set_message(cast_text(n.fullName()))
            channels = [cast_text(i) for i in n.channels()]
            if not ("forward.u" in channels and "forward.v" in channels):
                nuke.message(
                    cast_str(
                        "节点 {} 缺少 forward.u 和 forward.v 通道，将跳过".format(n.name()),
                    )
                )
                continue
            create(n, base, start, end, interval)
