# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Sequence, List

import random

import nuke

from wulifang._util import (
    assert_isinstance,
    cast_str,
    cast_int,
)
from ._node_list import NodeList
from ._is_node_inside_backdrop import is_node_inside_backdrop


def create_backdrop(nodes):
    # type: (Sequence[nuke.Node]) -> nuke.BackdropNode
    """
    Automatically puts a backdrop behind the selected nodes.

    The backdrop will be just big enough to fit all the select nodes in, with room
    at the top for some text in a large font.
    """
    if not nodes:
        return assert_isinstance(nuke.nodes.BackdropNode(), nuke.BackdropNode)
    nodes = NodeList(nodes)

    z_order = 0
    selected_backdrop_nodes = nuke.selectedNodes(cast_str("BackdropNode"))
    non_selected_backdrop_nodes = []  # type: List[nuke.Node]
    # if there are backdropNodes selected put the new one immediately behind the farthest one
    if selected_backdrop_nodes:
        z_order = (
            min(
                [
                    cast_int(node.knob(cast_str("z_order")).value())
                    for node in selected_backdrop_nodes
                ]
            )
            - 1
        )
    else:
        # otherwise (no backdrop in selection) find the nearest backdrop
        # if exists and set the new one in front of it
        non_selected_backdrop_nodes = nuke.allNodes(cast_str("BackdropNode"))
    for non_backdrop in nodes:
        for backdrop in non_selected_backdrop_nodes:
            if is_node_inside_backdrop(non_backdrop, backdrop):
                z_order = max(
                    z_order, cast_int(backdrop.knob(cast_str("z_order")).value()) + 1
                )

    # Expand the bounds to leave a little border. Elements are offsets for left,
    # top, right and bottom edges respectively
    left, top, right, bottom = (-10, -80, 10, 10)

    n = nuke.nodes.BackdropNode(
        xpos=nodes.xpos + left,
        bdwidth=nodes.width + (right - left),
        ypos=nodes.ypos + top,
        bdheight=nodes.height + (bottom - top),
        tile_color=int((random.random() * (16 - 10))) + 10,
        note_font_size=42,
        z_order=z_order,
    )

    return assert_isinstance(n, nuke.BackdropNode)
