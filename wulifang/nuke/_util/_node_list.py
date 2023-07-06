# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import List, Set, Iterable

    NodeListBase = List[nuke.Node]
else:
    NodeListBase = list

from wulifang._util import cast_str, cast_text
from ._node_deep_dependencies import node_deep_dependencies


class NodeList(NodeListBase):  # type: ignore
    """Optimized list for nuke.Node."""

    def __init__(self, nodes=[]):
        # type: (Iterable[nuke.Node]) -> None
        NodeListBase.__init__(self, nodes)

    @property
    def xpos(self):
        # type: () -> int
        """The x position."""
        return min(n.xpos() for n in self)

    @xpos.setter
    def xpos(self, value):
        # type: (int) -> None
        extend_x = value - self.xpos
        for n in self:
            xpos = n.xpos() + extend_x
            n.setXpos(xpos)

    @property
    def ypos(self):
        # type: () -> int
        """The y position."""
        return min([node.ypos() for node in self])

    @ypos.setter
    def ypos(self, value):
        # type: (int) -> None
        extend_y = value - self.ypos
        for n in self:
            ypos = n.ypos() + extend_y
            n.setYpos(ypos)

    @property
    def width(self):
        """The total width of all nodes."""
        return self.right - self.xpos

    @property
    def max_width(self):
        """The node width max value in this."""
        return max(n.screenWidth() for n in self)

    @property
    def height(self):
        """The total height of all nodes."""
        return self.bottom - self.ypos

    @property
    def bottom(
        self,  # type: List[nuke.Node]
    ):
        # type: () -> int
        """The bottom border of all nodes."""
        return max([node.ypos() + node.screenHeight() for node in self])

    @bottom.setter
    def bottom(self, value):
        # type: (int) -> None
        extend_y = value - self.bottom
        for n in self:
            ypos = n.ypos() + extend_y
            n.setYpos(ypos)

    @property
    def right(
        self,  # type: List[nuke.Node]
    ):
        # type: () -> int
        """The right border of all nodes."""
        return max(n.xpos() + n.screenWidth() for n in self)

    @right.setter
    def right(self, value):
        # type: (int) -> None
        extend_x = value - self.right
        for n in self:
            xpos = n.xpos() + extend_x
            n.setXpos(xpos)

    def end_nodes(self):
        """Return Nodes that has no downstream founded in given nodes."""

        ret_set = set(
            (n for n in self if cast_text(n.Class()) not in ("Viewer",)),
        )  # type: Set[nuke.Node]
        other = list(n for n in self if n not in ret_set)

        for n in list(ret_set):
            dep = n.dependencies(nuke.INPUTS)
            if set(self).intersection(dep):
                ret_set.difference_update(dep)
        ret = sorted(
            ret_set, key=lambda x: len(node_deep_dependencies(x)), reverse=True
        )
        ret.extend(other)
        return ret

    def disable(
        self,  # type: List[nuke.Node]
    ):
        """Disable all."""

        for n in self:
            try:
                n[cast_str("disable")].setValue(True)
            except NameError:
                continue

    def enable(self):
        """Enable all."""

        for n in self:
            try:
                n[cast_str("disable")].setValue(False)
            except NameError:
                continue

    def select(self):
        s = set(self)
        for n in nuke.selectedNodes():
            if n not in s:
                n.setSelected(False)
        self.set_selected(True)

    def set_selected(self, v):
        # type: (bool) -> None

        for n in self:
            n.setSelected(v)
