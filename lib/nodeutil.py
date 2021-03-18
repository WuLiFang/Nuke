# -*- coding=UTF-8 -*-
"""Nuke node utility.  """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

import cast_unknown as cast

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import List, Set, Iterable, Union


class Nodes(
    list
):
    """Optimized list for nuke.Node.  """

    def __init__(self, nodes=None):
        super(Nodes, self).__init__(cast.iterable(nodes))   # type: ignore

    @property
    def xpos(self):
        # type: () -> int
        """The x position.  """
        return min(cast.instance(n, nuke.Node).xpos() for n in self)

    @xpos.setter
    def xpos(self, value):
        extend_x = value - self.xpos
        for n in self:
            n = cast.instance(n, nuke.Node)
            xpos = n.xpos() + extend_x
            n.setXpos(xpos)

    @property
    def ypos(self):
        """The y position.  """
        return min([cast.instance(node, nuke.Node).ypos() for node in self])

    @ypos.setter
    def ypos(self, value):
        extend_y = value - self.ypos
        for n in self:
            n = cast.instance(n, nuke.Node)
            ypos = n.ypos() + extend_y
            n.setYpos(ypos)

    @property
    def width(self):
        """The total width of all nodes.  """
        return self.right - self.xpos

    @property
    def max_width(self):
        """The node width max value in this."""
        return max(cast.instance(n, nuke.Node).screenWidth() for n in self)

    @property
    def height(self):
        """The total height of all nodes.  """
        return self.bottom - self.ypos

    @property
    def bottom(
        self,  # type: List[nuke.Node]
    ):
        # type: () -> int
        """The bottom border of all nodes.  """
        return max([node.ypos() + node.screenHeight()
                    for node
                    in self

                    ])

    @bottom.setter
    def bottom(self, value):
        extend_y = value - self.bottom
        for n in self:
            n = cast.instance(n, nuke.Node)
            ypos = n.ypos() + extend_y
            n.setYpos(ypos)

    @property
    def right(
        self,  # type: List[nuke.Node]

    ):
        # type: () -> int
        """The right border of all nodes.  """
        return max(n.xpos() + n.screenWidth() for n in self)

    @right.setter
    def right(self, value):
        extend_x = value - self.right
        for n in self:
            n = cast.instance(n, nuke.Node)
            xpos = n.xpos() + extend_x
            n.setXpos(xpos)

    def set_position(self, xpos=None, ypos=None):
        """Move nodes to given @xpos, @ypos.  """
        if xpos:
            self.xpos = xpos
        if ypos:
            self.ypos = ypos

    def autoplace(self):
        """Auto place nodes."""

        from orgnize import autoplace
        _ = autoplace(self)

    def endnodes(self):
        """Return Nodes that has no downstream founded in given nodes.  """

        ret_set = set(n for n in self if cast.instance(
            n, nuke.Node).Class() not in ('Viewer',),

        )  # type: Set[nuke.Node]
        other = list(n for n in self if n not in ret_set)

        for n in list(ret_set):
            n = cast.instance(n, nuke.Node)
            dep = n.dependencies(nuke.INPUTS)
            if set(self).intersection(dep):
                ret_set.difference_update(dep)
        ret = sorted(ret_set, key=lambda x: len(
            get_upstream_nodes(x)), reverse=True)
        ret.extend(other)
        return ret

    def disable(
        self,  # type: List[nuke.Node]
    ):
        """Disable all.  """

        for n in self:
            try:
                _ = n[b'disable'].setValue(True)
            except NameError:
                continue

    def enable(self):
        """Enable all.  """

        for n in self:
            n = cast.instance(n, nuke.Node)
            try:
                _ = n[b'disable'].setValue(False)
            except NameError:
                continue


def get_upstream_nodes(
    nodes,  # type: Union[Iterable[nuke.Node], nuke.Node]
    flags=nuke.INPUTS | nuke.HIDDEN_INPUTS,  # type: int
):
    """ Return all nodes in the tree of the node. """
    ret = set()
    if isinstance(nodes, nuke.Node):
        nodes = [nodes]

    nodes = list(nodes)
    while nodes:
        deps = nuke.dependencies(nodes, flags)
        nodes = [n for n in deps if n not in ret and n not in nodes]
        ret.update(set(deps))
    return ret


def is_node_deleted(node):
    # type: (nuke.Node) -> bool
    """Check if node already deleted.  """

    try:
        _ = repr(node)
        return False
    except ValueError:
        return True
