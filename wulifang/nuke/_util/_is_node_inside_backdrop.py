# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke


def is_node_inside_backdrop(node, backdrop):
    # type: (nuke.Node, nuke.Node) -> bool
    """Returns true if node geometry is inside backdropNode otherwise returns false"""
    top_left_node = [node.xpos(), node.ypos()]
    top_left_backdrop = [backdrop.xpos(), backdrop.ypos()]
    bottom_right_node = [
        node.xpos() + node.screenWidth(),
        node.ypos() + node.screenHeight(),
    ]
    bottom_right_backdrop = [
        backdrop.xpos() + backdrop.screenWidth(),
        backdrop.ypos() + backdrop.screenHeight(),
    ]

    top_left = (top_left_node[0] >= top_left_backdrop[0]) and (
        top_left_node[1] >= top_left_backdrop[1]
    )
    bottom_right = (bottom_right_node[0] <= bottom_right_backdrop[0]) and (
        bottom_right_node[1] <= bottom_right_backdrop[1]
    )

    return top_left and bottom_right
