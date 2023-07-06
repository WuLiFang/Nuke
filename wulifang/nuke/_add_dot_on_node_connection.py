# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterable

import nuke

from wulifang._util import cast_text, cast_str


def add(_nodes):
    # type: (Iterable[nuke.Node]) -> None
    """Add dots to organize node tree."""

    def add_to_input(
        output_node,  # type: nuke.Node
        input_num,  # type: int
    ):  # type: (...) -> None
        input_node = output_node.input(input_num)
        if (
            not input_node
            or cast_text(input_node.Class()) in ["Dot"]
            or abs(output_node.xpos() - input_node.xpos()) < output_node.screenWidth()
            or abs(output_node.ypos() - input_node.ypos()) <= output_node.screenHeight()
        ):
            return
        if (
            cast_text(output_node.Class()) in ["Viewer"]
            or output_node[cast_str("hide_input")].value()
        ):
            return

        dot = nuke.nodes.Dot(inputs=[input_node])
        output_node.setInput(input_num, dot)
        dot.setXYpos(
            int(
                input_node.xpos() + input_node.screenWidth() / 2 - dot.screenWidth() / 2
            ),
            int(
                output_node.ypos()
                + output_node.screenHeight() / 2
                - dot.screenHeight() / 2
                - (dot.screenHeight() + 5) * input_num
            ),
        )

    def add_to_all_input(node):
        # type: (nuke.Node) -> None
        for input_num in range(node.inputs()):
            add_to_input(node, input_num)

    for n in _nodes:
        if cast_text(n.Class()) in ["Dot"]:
            continue
        add_to_all_input(n)
