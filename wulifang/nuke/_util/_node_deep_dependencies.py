# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Union, Iterable

import nuke


def node_deep_dependencies(
    nodes,  # type: Union[Iterable[nuke.Node], nuke.Node]
    flags=nuke.INPUTS | nuke.HIDDEN_INPUTS,  # type: int
):
    # type: (...) -> set[nuke.Node]
    """Return all nodes in the tree of the node."""
    ret = set()  # type: set[nuke.Node]
    if isinstance(nodes, nuke.Node):
        nodes = [nodes]

    nodes = list(nodes)
    while nodes:
        deps = nuke.dependencies(nodes, flags)
        nodes = [n for n in deps if n not in ret and n not in nodes]
        ret.update(set(deps))
    return ret
