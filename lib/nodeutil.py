# -*- coding=UTF-8 -*-
"""Nuke node utility.  """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke


class Nodes(list):
    """Optmized list for nuke.Node.  """

    def __init__(self, nodes=None):
        if nodes is None:
            nodes = []
        if isinstance(nodes, nuke.Node):
            nodes = [nodes]

        list.__init__(self, nodes)

    @property
    def xpos(self):
        """The x position.  """
        return min(n.xpos() for n in self)

    @xpos.setter
    def xpos(self, value):
        extend_x = value - self.xpos
        for n in self:
            xpos = n.xpos() + extend_x
            n.setXpos(xpos)

    @property
    def ypos(self):
        """The y position.  """
        return min([node.ypos() for node in self])

    @ypos.setter
    def ypos(self, value):
        extend_y = value - self.ypos
        for n in self:
            ypos = n.ypos() + extend_y
            n.setYpos(ypos)

    @property
    def width(self):
        """The total width of all nodes.  """
        return self.right - self.xpos

    @property
    def max_width(self):
        """The node width max value in this."""
        return max(n.screenWidth() for n in self)

    @property
    def height(self):
        """The total height of all nodes.  """
        return self.bottom - self.ypos

    @property
    def bottom(self):
        """The bottom border of all nodes.  """
        return max([node.ypos() + node.screenHeight()
                    for node in self])

    @bottom.setter
    def bottom(self, value):
        extend_y = value - self.bottom
        for n in self:
            ypos = n.ypos() + extend_y
            n.setYpos(ypos)

    @property
    def right(self):
        """The right border of all nodes.  """
        return max(n.xpos() + n.screenWidth() for n in self)

    @right.setter
    def right(self, value):
        extend_x = value - self.right
        for n in self:
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
        autoplace(self)

    def endnodes(self):
        """Return Nodes that has no downstream founded in given nodes.  """

        ret = set(n for n in self if n.Class() not in ('Viewer',))
        other = list(n for n in self if n not in ret)

        for n in list(ret):
            dep = n.dependencies(nuke.INPUTS)
            if set(self).intersection(dep):
                ret.difference_update(dep)
        ret = sorted(ret, key=lambda x: len(
            get_upstream_nodes(x)), reverse=True)
        ret.extend(other)
        return ret

    def disable(self):
        """Disable all.  """

        for n in self:
            try:
                n['disable'].setValue(True)
            except NameError:
                continue

    def enable(self):
        """Enable all.  """

        for n in self:
            try:
                n['disable'].setValue(False)
            except NameError:
                continue


def get_upstream_nodes(nodes, flags=nuke.INPUTS | nuke.HIDDEN_INPUTS):
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
    """Check if node already deleted.  """

    try:
        repr(node)
        return False
    except ValueError:
        return True
