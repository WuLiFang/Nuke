# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke


def replace_node(
    _node,  # type: nuke.Node
    _repl,  # type: nuke.Node
):  # type: (...) -> None
    """Replace a node with another in node graph.

    Args:
        node: Node to be replaced.
        repl_node: Node to replace.
    """

    nodes = _node.dependent(nuke.INPUTS | nuke.HIDDEN_INPUTS, False)
    for n in nodes:
        for i in range(n.inputs()):
            if n.input(i) is _node:
                n.setInput(i, _repl)
