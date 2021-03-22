# -*- coding=UTF-8 -*-
"""Map rotopaint shape by uv and append a STMap.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import cast_unknown as cast
import nuke
from nuke.curvelib import CVec3
import nuke.curveknob
import _rotopaint

from edit import replace_node
from nuketools import undoable_func
from rotopaint_tools import (iter_layer, iter_shape_point,
                             iter_shapes_in_layer)
from wlf.progress import progress
from wlf_tools.progress import CustomMessageProgressHandler

UV_LAYER_NAME = "uv_map"
GENERATED_SHAPE_SUFFIX = ".UVMap"


def _uv_map_rotopaint_anim_point_time(uv, point, u_channel, v_channel, frame):
    pos_before = point.getPosition(frame)
    w, h = uv.width(), uv.height()
    u, v = uv.sample(
        u_channel,
        pos_before.x,
        pos_before.y,
        frame=frame,
    ), uv.sample(
        v_channel,
        pos_before.x,
        pos_before.y,
        frame=frame,
    )
    pos_after = CVec3(u*w, v*h)

    def _job():
        point.addPositionKey(frame, pos_after)
    return _job


def _uv_map_rotopaint_anim_point(uv, point, u_channel, v_channel):
    times = point.getControlPointKeyTimes()
    for i in times:
        yield _uv_map_rotopaint_anim_point_time(
            uv, point, u_channel, v_channel, i,
        )


def _uv_map_rotopaint_shape_point(uv, point, u_channel, v_channel):
    # we need compute all points before apply any,
    # because center move will cause sample result change for relative point.
    deferred_jobs = []
    for i in iter_shape_point(point):
        deferred_jobs.extend(
            _uv_map_rotopaint_anim_point(
                uv, i, u_channel, v_channel
            ),
        )

    for i in deferred_jobs:
        i()


def _uv_map_rotopaint_shape(uv, shape, u_channel, v_channel):
    for i in shape:
        _uv_map_rotopaint_shape_point(uv, i, u_channel, v_channel)


def _iter_matched_shape(layer, extra):
    for i in iter_layer(layer):
        if not isinstance(i, nuke.curveknob.Shape):
            continue
        attrs = i.getAttributes()
        visible_curve = attrs.getCurve(attrs.kVisibleAttribute)
        if (not visible_curve.constantValue
                or visible_curve.getNumberOfKeys() > 0):
            continue
        yield i


def _remove_generated_shape(layer):
    indexes = []
    raw_names = set()
    for index, i in enumerate(iter_layer(layer)):
        if isinstance(i, nuke.curveknob.Layer):
            raw_names.update(_remove_generated_shape(layer))
            continue
        if not isinstance(i, nuke.curveknob.Shape):
            continue
        if not i.name.endswith(GENERATED_SHAPE_SUFFIX):
            continue
        indexes.append(index)
        raw_names.add(i.name[:-len(GENERATED_SHAPE_SUFFIX)])
    indexes.reverse()
    for i in indexes:
        layer.remove(i)
    return raw_names


def _recover_raw_shape_by_name(layer, names):
    for i in iter_shapes_in_layer(layer):
        if i.name not in names:
            continue
        attrs = i.getAttributes()
        attrs.getCurve(attrs.kVisibleAttribute).constantValue = True
        i.locked = False


@undoable_func("RotoPaint UVMap")
def uv_map_rotopaint(rotopaint, u_channel, v_channel):
    assert isinstance(rotopaint, nuke.Node)
    assert rotopaint.Class() == "RotoPaint", (
        "should be rotopaint, got {}".format(rotopaint.Class()))

    uv = rotopaint
    channels = uv.channels()
    rotopaint_output = rotopaint[b"output"].value()
    if not (u_channel in channels and v_channel in channels):
        uv = nuke.nodes.ShuffleCopy(
            inputs=[rotopaint.input(0), rotopaint.input(0)],
            out=UV_LAYER_NAME,
            label=b"uv map",
        )
        uv = nuke.nodes.Remove(
            inputs=[uv],
            channels=rotopaint_output,
            label=rotopaint_output
        )
        _ = rotopaint.setInput(0, uv)

    layer = cast.instance(rotopaint[b"curves"], _rotopaint.RotoKnob).rootLayer
    raw_shape_names = _remove_generated_shape(layer)
    _recover_raw_shape_by_name(layer, raw_shape_names)

    for i in progress(
            list(_iter_matched_shape(layer, raw_shape_names)),
            rotopaint.name(),
            handler=CustomMessageProgressHandler(
                lambda i: i.name,
            ),
    ):
        v = i.clone()
        v.name = i.name + cast.binary(GENERATED_SHAPE_SUFFIX)

        attrs = i.getAttributes()
        attrs.getCurve(attrs.kVisibleAttribute).constantValue = False
        i.locked = True

        _uv_map_rotopaint_shape(
            uv,
            v,
            u_channel,
            v_channel,
        )

    if not any(i.Class() == "STMap" for i in rotopaint.dependent()):
        replace_node(
            rotopaint,
            nuke.nodes.STMap(
                inputs=[rotopaint, rotopaint],
                channels=rotopaint_output,
                uv=UV_LAYER_NAME,
            )
        )


def uv_map_selected_rotopaint():
    nodes = nuke.selectedNodes(b"RotoPaint")
    if not nodes:
        nuke.message(cast.binary("请选中RotoPaint节点"))
        return

    # Node.sample need a transformed position when using proxy
    _ = nuke.Root()[b"proxy"].setValue(False)

    uv_layer = nuke.Layer(cast.binary(UV_LAYER_NAME))
    if len(uv_layer.channels()) < 2:
        uv_layer = nuke.Layer(
            cast.binary(UV_LAYER_NAME),
            [cast.binary("{}.{}".format(UV_LAYER_NAME, i))
             for i in ("u", "v")],
        )
    uv_channels = uv_layer.channels()
    assert len(uv_channels) >= 2, \
        "uv layer should has >=2 channels, got {}".format(uv_channels)
    u_channel = uv_channels[0]
    v_channel = uv_channels[1]

    for n in progress(
            nodes, "RotoPaint UV映射",
            handler=CustomMessageProgressHandler(
                lambda i: i.name()
            ),
    ):
        uv_map_rotopaint(n, u_channel, v_channel)
