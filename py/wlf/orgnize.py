# -*- coding=UTF-8 -*-
"""Orgnize nodes layout.  """
import random

import nuke

from .node import get_upstream_nodes

__version__ = '0.4.4'


def autoplace(nodes=None):
    """Auto place nodes."""
    if not nodes:
        nodes = nuke.allNodes()
    nodes = Nodes(nodes)
    xpos, ypos = nodes.xpos, nodes.ypos
    nodes.autoplace()
    if nodes != nuke.allNodes():
        nodes.xpos, nodes.ypos = xpos, ypos


def is_node_inside(node, backdrop):
    """Returns true if node geometry is inside backdropNode otherwise returns false"""
    topleft_node = [node.xpos(), node.ypos()]
    topleft_backdrop = [backdrop.xpos(), backdrop.ypos()]
    bottomright_node = [node.xpos() + node.screenWidth(),
                        node.ypos() + node.screenHeight()]
    bottomright_backdrop = [
        backdrop.xpos() + backdrop.screenWidth(),
        backdrop.ypos() + backdrop.screenHeight()]

    topleft = (topleft_node[0] >= topleft_backdrop[0]) and (
        topleft_node[1] >= topleft_backdrop[1])
    bottomright = (bottomright_node[0] <= bottomright_backdrop[0]) and (
        bottomright_node[1] <= bottomright_backdrop[1])

    return topleft and bottomright


class Nodes(list):
    """Geometry boder size of @nodes.  """
    y_gap = 10
    x_gap = 10
    placed_nodes = set()

    def __init__(self, nodes=None):
        if nodes is None:
            nodes = []
        if isinstance(nodes, nuke.Node):
            nodes = [nodes]
        if isinstance(nodes, Branches):
            nodes = nodes.nodes

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
        backdrops_dict = {n: Nodes(n.getNodes())
                          for n in self if n.Class() == 'BackdropNode'}

        Nodes.placed_nodes.clear()

        for n in self.endnodes():
            branches = Branches(
                n, nodes=list(n for n in self if n not in Nodes.placed_nodes))

            branches.autoplace()
            if Nodes.placed_nodes and branches.nodes:
                branches.nodes.xpos = Nodes(Nodes.placed_nodes).right + 20
            Nodes.placed_nodes.update(set(branches.nodes))

        left, top, right, bottom = (-10, -80, 10, 10)
        for backdrop, nodes_in_backdrop in backdrops_dict.items():
            if not nodes_in_backdrop:
                continue
            up_nodes = Nodes(n for n in get_upstream_nodes(nodes_in_backdrop)
                             if n.ypos() < nodes_in_backdrop.bottom
                             and n not in nodes_in_backdrop)
            if up_nodes:
                up_nodes.bottom = nodes_in_backdrop.ypos + top
            up_nodes.extend(nodes_in_backdrop)
            up_nodes.ypos -= bottom

        for backdrop, nodes_in_backdrop in backdrops_dict.items():
            if not nodes_in_backdrop:
                continue
            backdrop.setXYpos(nodes_in_backdrop.xpos + left,
                              nodes_in_backdrop.ypos + top)
            backdrop['bdwidth'].setValue(
                nodes_in_backdrop.width + (right - left))
            backdrop['bdheight'].setValue(
                nodes_in_backdrop.height + (bottom - top))

        nuke.Root().setModified(True)

    def endnodes(self):
        """Return Nodes that has no contained downstream founded in given nodes.  """
        available_nodes = Nodes(
            n for n in self if n.Class() not in ('Viewer',))
        ret = Nodes(n for n in available_nodes
                    if all(n not in available_nodes for n in n.dependent(nuke.INPUTS)))
        ret.sort(key=lambda x: len(get_upstream_nodes(x)), reverse=True)
        ret.extend(n for n in self if n not in available_nodes)
        return ret


def autoplace_backdrop(backdrop):
    """autoplace nodes by @backdrop.  """
    assert backdrop.Class() == 'BackdropNode', '请选择BackdropNode节点'
    nodes = Nodes(backdrop.getNodes())
    other_nodes = list(n for n in nuke.allNodes()
                       if n not in nodes and n is not backdrop)
    width, height = nodes.width, nodes.height
    map(autoplace, nodes)
    extend_x, extend_y = nodes.width - width, nodes.height - height
    for n in other_nodes:
        xpos = n.xpos()
        ypos = n.ypos()
        xpos = xpos + extend_x if xpos > nodes.xpos else xpos
        ypos = ypos + extend_y if ypos > nodes.ypos else ypos
        n.setXYpos(xpos, ypos)
    backdrop['bdwidth'].setValue(backdrop['bdwidth'].value() + extend_x)
    backdrop['bdheight'].setValue(backdrop['bdheight'].value() + extend_y)


class Branch(Nodes):
    """A branch is a list of connected nodes. (e.g. [node1, node2, ... node_n]).  """
    depth = 0
    _parent_branch = None
    _parent_nodes = None
    _expanded = None
    big_branch_thershold = 10

    def __init__(self, node=None):
        if isinstance(node, nuke.Node):
            node = [node]
        elif node is None:
            node = []
        Nodes.__init__(self, node)

    def expand(self, nodes=None):
        """Expand self to upstream 1 time, can limit in @nodes.  """

        if self.expanded:
            return False
        ret = Branches()
        nodes = nodes or nuke.allNodes()
        input_nodes = self[-1].dependencies(nuke.INPUTS)
        for index, input_node in enumerate(input_nodes):
            if input_node not in nodes:
                continue
            if index == 0:
                branch = self
            else:
                branch = Branch()
                branch.parent_nodes = Nodes(self[:-1])
                branch.parent_branch = self
                branch.depth = self.depth + len(self)
            branch.append(input_node)
            ret.append(branch)
        return ret

    @property
    def expanded(self):
        """Return if this branch is expanded to end.  """
        if not self._expanded:
            startnode = self[-1]
            input_nodes = startnode.dependencies(nuke.INPUTS)
            self._expanded = not bool(input_nodes)
        return self._expanded

    def new_nodes(self):
        """Return nodes that need to be autoplaced in this branch.  """
        return Nodes(n for n in self if n not in Branches.placed_nodes)

    def base_node(self, length_filter=None):
        """Return the base node this branch splitted from.  """
        if length_filter is None:
            length_filter = self.big_branch_thershold
        ret = self[0]
        branch = self
        while branch:
            if branch.parent_nodes:
                ret = branch.parent_nodes[-1]
            else:
                break
            branch = branch.parent_branch
            if len(branch) >= length_filter:
                break
        return ret

    def prev_nodes(self):
        """Return previous autoplaced nodes.  """
        ret = Nodes()
        if self.parent_nodes:
            ret = Nodes(n for n in get_upstream_nodes(self.base_node())
                        if n not in self.new_nodes()
                        and n in Branches.placed_nodes)
        return ret

    def autoplace(self):
        """Autoplace nodes in this branch.  """
        nodes = self.new_nodes()
        if not nodes:
            return

        # nuke.zoomToFitSelected()
        # if not nuke.ask(str(self.base_node().name())):
        #     raise RuntimeError

        # Y-axis.
        ypos = 0
        for n in nodes:
            ypos -= n.screenHeight() + self.y_gap
            n.setYpos(ypos)
        if len(nodes) < self.big_branch_thershold:
            # Place nodes accroding parent.
            if self.parent_nodes:
                nodes.bottom = self.parent_nodes.ypos - self.y_gap
            # Move other nodes up.
            up_nodes = Nodes(n for n in self.prev_nodes()
                             if Nodes(n).bottom <= nodes.bottom)
            if up_nodes:
                up_nodes.bottom = nodes.ypos - nodes.y_gap
        elif self.parent_nodes:
            nodes.bottom = self.parent_nodes.ypos - self.y_gap

        # X-axis.
        if len(nodes) >= self.big_branch_thershold and Branches.placed_nodes:
            xpos = Nodes(Branches.placed_nodes).right + self.x_gap * 50
        else:
            xpos = 0

        if self.parent_nodes:
            left_nodes = Nodes(n for n in self.prev_nodes()
                               if n.ypos() >= nodes.ypos
                               and Nodes(n).bottom <= nodes.bottom)
            if left_nodes:
                xpos = max([left_nodes.right + self.x_gap, xpos])

        if self.parent_nodes:
            xpos = max([Nodes(self.parent_nodes[-1]).right + self.x_gap, xpos])
        for n in nodes:
            n.setXpos(xpos + (nodes.max_width - n.screenWidth()) / 2)

    @property
    def parent_nodes(self):
        """The nodes branch expand from."""
        return self._parent_nodes

    @parent_nodes.setter
    def parent_nodes(self, value):
        if not isinstance(value, list):
            raise TypeError('Expected list type.  ')
        self._parent_nodes = Nodes(value)

    @property
    def parent_branch(self):
        """The branch this branch expand from."""
        return self._parent_branch

    @parent_branch.setter
    def parent_branch(self, value):
        if not isinstance(value, Branch):
            raise TypeError('Expected Branch type.  ')
        self._parent_branch = value

    def total_length(self):
        """Return length of this branch and branched to the start. """
        parent_branch = self.parent_branch
        ret = len(self)
        while parent_branch:
            ret += len(parent_branch)
            parent_branch = parent_branch.parent_branch
        return ret

    def __str__(self):
        return 'Branch< {} >'.format(' -> '.join(n.name() for n in self))


class Branches(list):
    """A branches is a list of branch. (e.g. [branch1, branch2, ... branch_n]).  """
    placed_nodes = set()

    def __init__(self, branches=None, nodes=None):
        if isinstance(branches, nuke.Node):
            branches = [Branch(branches)]
        elif isinstance(branches, Branch):
            branches = [branches]
        elif branches is None:
            branches = []
        self._nodes = nodes or nuke.allNodes()
        list.__init__(self, branches)
        if self:
            self.expand()

            # for i in self:

    def expand(self):
        """Expand all branches to the end.  """
        not_done = True
        task = nuke.ProgressTask('分析结构')
        count = 0
        while not_done:
            task.setMessage('向上{}层节点'.format(count))
            if task.isCancelled():
                raise RuntimeError('Cancelled')
            count += 1
            not_done = False
            itering = list(self)
            del self[:]
            all_num = len(itering)
            for index, branch in enumerate(itering):
                if count >= 50:
                    task.setProgress(index * 100 // all_num)
                expanded = branch.expand(nodes=self._nodes)
                if expanded:
                    not_done = True
                    self.extend(expanded)
                else:
                    self.append(branch)
            self._remove_duplicated()
        tested = set()
        for branch in self:
            for i in tested:
                if i in branch:
                    branch.remove(i)
                tested.add(i)

    def _remove_duplicated(self):
        for branch in list(self):
            if any(set(branch).issubset(set(i)) for i in list(self) if i is not branch):
                self.remove(branch)

    def autoplace(self):
        """Auto place branches.  """
        Branches.placed_nodes.clear()
        for branch in self:
            branch.autoplace()
            Branches.placed_nodes.update(branch)

    def __str__(self):
        return 'Branches[ {} ]'.format(', '.join(str(i) for i in self))

    def __contains__(self, operand):
        if isinstance(operand, Branch):
            return list.__contains__(self, operand)
        elif isinstance(operand, nuke.Node):
            return any(Branch.__contains__(i, operand) for i in self)
        else:
            raise TypeError

    def find(self, node):
        """Return first @node contained branch. """
        for branch in self:
            if node in branch:
                return branch

    @property
    def nodes(self):
        """The nodes in this."""
        ret = []
        for i in self:
            ret.extend(i)
        ret = set(ret)
        return Nodes(ret)


def create_backdrop(nodes, autoplace_nodes=False):
    '''
    Automatically puts a backdrop behind the selected nodes.

    The backdrop will be just big enough to fit all the select nodes in, with room
    at the top for some text in a large font.
    '''
    if autoplace_nodes:
        map(nuke.autoplace, nodes)
    if not nodes:
        return nuke.nodes.BackdropNode()
    nodes = Nodes(nodes)

    z_order = 0
    selected_backdropnodes = nuke.selectedNodes("BackdropNode")
    # if there are backdropNodes selected put the new one immediately behind the farthest one
    if selected_backdropnodes:
        z_order = min([node.knob("z_order").value()
                       for node in selected_backdropnodes]) - 1
    else:
        # otherwise (no backdrop in selection) find the nearest backdrop
        # if exists and set the new one in front of it
        non_selected_backdropnodes = nuke.allNodes("BackdropNode")
    for non_backdrop in nodes:
        for backdrop in non_selected_backdropnodes:
            if is_node_inside(non_backdrop, backdrop):
                z_order = max(z_order, backdrop.knob("z_order").value() + 1)

    # Expand the bounds to leave a little border. Elements are offsets for left,
    # top, right and bottom edges respectively
    left, top, right, bottom = (-10, -80, 10, 10)

    n = nuke.nodes.BackdropNode(xpos=nodes.xpos + left,
                                bdwidth=nodes.width + (right - left),
                                ypos=nodes.ypos + top,
                                bdheight=nodes.height + (bottom - top),
                                tile_color=int(
                                    (random.random() * (16 - 10))) + 10,
                                note_font_size=42,
                                z_order=z_order)

    return n
