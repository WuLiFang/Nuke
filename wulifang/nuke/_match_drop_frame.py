# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang._util import (
    cast_text,
    cast_str,
    cast_int,
    cast_float,
    cast_list,
)
from wulifang.nuke._util import (
    undoable,
    knob_of,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Optional


def _get_timewarp_data(n, start, end, tolerance=0.001):
    # type: (nuke.Node, int, int ,float) -> list[int]
    """Get timewarp data from a node

    Args:
        n (nuke.Node): Node
        start (int): Start frame
        end (int): End frame
        tolerance (float, optional): Match tolerance. Defaults to 0.001.

    Returns:
        typing.List[int]: Data for timewarp.
    """

    nodes = []  # type: list[nuke.Node]
    ret = []  # type: list[int]
    try:

        n_time_offset = nuke.nodes.TimeOffset(inputs=[n], time_offset=1)
        nodes.append(n_time_offset)
        n_merge = nuke.nodes.Merge2(inputs=[n, n_time_offset], operation="difference")
        nodes.append(n_merge)
        n_curve_tool = nuke.nodes.CurveTool(
            inputs=[n_merge],
            avgframes=0,
            ROI="{} {} {} {}".format(0, 0, n.width(), n.height()),
        )
        nodes.append(n_curve_tool)

        nuke.execute(n_curve_tool, start, end)
        k = knob_of(n_curve_tool, "intensitydata", nuke.Array_Knob)
        source_f = start
        for f in range(start, end + 1):
            v = sum(cast_list(k.getValueAt(f))[:3]) / 3
            if v > tolerance:
                source_f = f
            ret.append(source_f)
    finally:
        for i in nodes:
            nuke.delete(i)
    return ret


def _create_timewarp(data, start=1):
    # type: (list[int], int) -> nuke.Node
    """Create time wrap from time wrap data.

    Args:
        data (typing.List[int]): Frame lookup list for each frame from start.
        start (int, optional): Start frame. Defaults to 1.

    Returns:
        nuke.nodes.TimeWarp: Created node.
    """
    curve_points = [(start, data[0])]  # type.List[type.Tuple[int, int]]
    end = start + len(data)
    for index, i in enumerate(data):
        f = start + index
        if curve_points[-1][1] == i and f < end:
            # skip same value (not apply to last frame)
            continue
        curve_points.append((f, i))

    n = nuke.nodes.TimeWarp(
        lookup="{{ curve K {}}}".format(
            " ".join("x{} {}".format(i[0], i[1]) for i in curve_points)
        )
    )

    return n


@undoable("匹配抽帧")
def dialog(n):
    # type: (nuke.Node) -> Optional[nuke.Node]
    """GUI dialog for `get_timewarp_data`

    Returns:
        type.Optional[nuke.node.TimeWarp]: created node
    """

    title = "抽帧匹配: {}".format(n.name())
    panel = nuke.Panel(cast_str("抽帧匹配: %s" % (cast_text(n.fullName()),)))
    key_start = cast_str("起始帧")
    key_end = cast_str("结束帧")
    key_tolerance = cast_str("阈值")
    panel.addExpressionInput(key_start, cast_str(n.firstFrame()))
    panel.addExpressionInput(key_end, cast_str(n.lastFrame()))
    panel.addExpressionInput(key_tolerance, cast_str("0.001"))

    if not panel.show():
        return

    start = cast_int(panel.value(key_start))
    end = cast_int(panel.value(key_end))
    tolerance = cast_float(panel.value(key_tolerance))

    data = _get_timewarp_data(n, start, end, tolerance)

    if len(set(data)) == len(data):
        nuke.message(cast_str("未检测到抽帧"))
        return

    timewarp = _create_timewarp(data, start)
    knob_of(timewarp, "label", nuke.String_Knob).setValue(cast_str(title))
    nuke.zoom(nuke.zoom() or 1, (timewarp.xpos(), timewarp.ypos()))
    return timewarp
