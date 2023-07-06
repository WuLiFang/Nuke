# # -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke
import nuke.curvelib
import nuke.curveknob

from wulifang._util import (
    cast_str,
    cast_text,
)
from wulifang.nuke._util import (
    iter_rotopaint_anim_control_point,
    iter_deep_rotopaint_shape,
    iter_deep_rotopaint_element,
    create_node,
    undoable,
    knob_of,
    Progress,
    RotoKnob,
    replace_node,
    RelativeRotopaintAnimControlPoint,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Union, Iterable, Iterator, Callable


UV_LAYER_NAME = "uv_map"
GENERATED_SHAPE_SUFFIX = ".UVMap"


def _uv_map_rotopaint_anim_point_time(uv, point, u_channel, v_channel, frame):
    # type: (nuke.Node, Union[nuke.curvelib.AnimControlPoint,RelativeRotopaintAnimControlPoint], Text, Text, float) -> Callable[[], None]
    pos_before = point.getPosition(frame)
    w, h = uv.width(), uv.height()
    u, v = uv.sample(
        cast_str(u_channel),
        pos_before.x,
        pos_before.y,
        frame=frame,
    ), uv.sample(
        cast_str(v_channel),
        pos_before.x,
        pos_before.y,
        frame=frame,
    )
    pos_after = nuke.curvelib.CVec3(u * w, v * h)

    def _job():
        point.addPositionKey(frame, pos_after)

    return _job


def _uv_map_rotopaint_anim_point(uv, point, u_channel, v_channel):
    # type: (nuke.Node, Union[nuke.curvelib.AnimControlPoint,RelativeRotopaintAnimControlPoint], Text, Text) -> Iterator[Callable[[], None]]
    times = point.getControlPointKeyTimes()
    for i in times:
        yield _uv_map_rotopaint_anim_point_time(
            uv,
            point,
            u_channel,
            v_channel,
            i,
        )


def _uv_map_rotopaint_shape_point(uv, point, u_channel, v_channel):
    # type: (nuke.Node, nuke.curveknob.ShapeControlPoint, Text,Text) -> None
    # we need compute all points before apply any,
    # because center move will cause sample result change for relative point.
    deferred_jobs = []  # type: list[Callable[[], None]]
    for i in iter_rotopaint_anim_control_point(point):
        deferred_jobs.extend(
            _uv_map_rotopaint_anim_point(uv, i, u_channel, v_channel),
        )

    for i in deferred_jobs:
        i()


def _uv_map_rotopaint_shape(uv, shape, u_channel, v_channel):
    # type: (nuke.Node, nuke.curveknob.Shape, Text,Text) -> None
    for i in shape:
        _uv_map_rotopaint_shape_point(uv, i, u_channel, v_channel)


def _iter_matched_shape(layer):
    # type: (nuke.curveknob.Layer) -> Iterator[nuke.curveknob.Shape]
    for i in iter_deep_rotopaint_shape(layer):
        attrs = i.getAttributes()
        visible_curve = attrs.getCurve(attrs.kVisibleAttribute)
        if not visible_curve.constantValue or visible_curve.getNumberOfKeys() > 0:
            continue
        yield i


def _remove_generated_shape(layer):
    # type: (nuke.curveknob.Layer) -> set[str]
    indexes = []  # type: list[int]
    raw_names = set()  # type: set[str]
    for index, i in enumerate(iter_deep_rotopaint_element(layer)):
        if isinstance(i, nuke.curveknob.Layer):
            raw_names.update(_remove_generated_shape(layer))
            continue
        if not isinstance(i, nuke.curveknob.Shape):
            continue
        if not cast_text(i.name).endswith(GENERATED_SHAPE_SUFFIX):
            continue
        indexes.append(index)
        raw_names.add(cast_text(i.name)[: -len(GENERATED_SHAPE_SUFFIX)])
    indexes.reverse()
    for i in indexes:
        layer.remove(i)
    return raw_names


def _recover_raw_shape_by_name(layer, names):
    # type: (nuke.curveknob.Layer, set[str]) -> None
    for i in iter_deep_rotopaint_shape(layer):
        if cast_text(i.name) not in names:
            continue
        attrs = i.getAttributes()
        attrs.getCurve(attrs.kVisibleAttribute).constantValue = True
        i.locked = False


def _create_one(rotopaint, u_channel, v_channel):
    # type: (nuke.Node, Text, Text) -> None
    assert rotopaint.Class() == "RotoPaint", "should be rotopaint, got %s" % (
        cast_text(rotopaint.Class()),
    )

    uv = rotopaint
    channels = list(map(cast_text, uv.channels()))
    rotopaint_output = cast_text(
        knob_of(rotopaint, "output", nuke.Channel_Knob).value()
    )
    if not (u_channel in channels and v_channel in channels):
        uv = create_node(
            "ShuffleCopy",
            "out %s" % (UV_LAYER_NAME,),
            inputs=[rotopaint.input(0), rotopaint.input(0)],
            label="uv map",
        )
        uv = create_node(
            "Remove",
            "channels %s" % (rotopaint_output,),
            label=rotopaint_output,
        )
        _ = rotopaint.setInput(0, uv)

    layer = knob_of(rotopaint, "curves", RotoKnob).rootLayer
    raw_shape_names = _remove_generated_shape(layer)
    _recover_raw_shape_by_name(layer, raw_shape_names)

    with Progress(cast_text(rotopaint.fullName())):
        for i in _iter_matched_shape(layer):
            v = i.clone()
            v.name = cast_str(cast_text(i.name) + (GENERATED_SHAPE_SUFFIX))

            attrs = i.getAttributes()
            attrs.getCurve(attrs.kVisibleAttribute).constantValue = False
            i.locked = True

            _uv_map_rotopaint_shape(
                uv,
                v,
                u_channel,
                v_channel,
            )

    if not any(cast_text(i.Class()) == "STMap" for i in rotopaint.dependent()):
        replace_node(
            rotopaint,
            nuke.nodes.STMap(
                inputs=[rotopaint, rotopaint],
                channels=rotopaint_output,
                uv=UV_LAYER_NAME,
            ),
        )


@undoable("RotoPaint UV 映射")
def create(_nodes):
    # type: (Iterable[nuke.Node]) -> None

    # Node.sample need a transformed position when using proxy
    knob_of(nuke.root(), "proxy", nuke.Boolean_Knob).setValue(False)

    uv_layer = nuke.Layer(cast_str(UV_LAYER_NAME))
    if len(uv_layer.channels()) < 2:
        uv_layer = nuke.Layer(
            cast_str(UV_LAYER_NAME),
            [cast_str("{}.{}".format(UV_LAYER_NAME, i)) for i in ("u", "v")],
        )
    uv_channels = uv_layer.channels()
    assert len(uv_channels) >= 2, "uv layer should has >=2 channels, got {}".format(
        uv_channels
    )
    u_channel = cast_text(uv_channels[0])
    v_channel = cast_text(uv_channels[1])

    with Progress("RotoPaint UV映射") as p:
        for n in _nodes:
            p.increase()
            if cast_text(n.Class()) != "RotoPaint":
                continue
            name = cast_text(n.fullName())
            p.set_message(name)
            _create_one(n, u_channel, v_channel)
