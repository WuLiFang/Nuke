# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterable, Optional, Tuple


from ._util import iter_deep_all_nodes
from .._util import cast_str, cast_text
import nuke


def find_max_bbox_node(nodes):
    # type: (Iterable[nuke.Node]) -> Tuple[Optional[nuke.Node], Optional[nuke.Node]]
    max_size = 0
    node = None
    leaf = None
    for i in nodes:
        if isinstance(i, nuke.Group):
            _, j = find_max_bbox_node(iter_deep_all_nodes(i))
        else:
            j = i
        if not j:
            continue
        bbox = j.bbox()
        size = bbox.w() * bbox.h()
        if size > max_size:
            max_size = size
            node = i
            leaf = j

    return node, leaf


def show_max_bbox_node():
    node, leaf = find_max_bbox_node(nuke.selectedNodes())
    if not node or not leaf:
        nuke.message(cast_str("请先选中节点"))
        return
    nuke.zoom(1.0, (node.xpos(), node.ypos()))

    nuke.message(
        cast_str(
            "当前选择中 BBox 最大的节点是 '%s' (%dx%d)"
            % (cast_text(leaf.fullName()), leaf.bbox().w(), leaf.bbox().h())
        )
    )
