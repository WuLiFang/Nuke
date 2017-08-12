# -*- coding=UTF-8 -*-
"""Orgnize nodes layout.  """
import random

import nuke

__version__ = '0.1.3'


def autoplace(nodes=None):
    """Auto place nodes."""

    backdrops_dict = {n: Nodes(n.getNodes())
                      for n in nuke.allNodes('BackdropNode')}

    nodes = nodes or list(n for n in nuke.allNodes()
                          if not any(n for n in n.dependent(nuke.INPUTS)
                                     if n.Class() not in ('Viewer', 'BackdropNode'))
                          and n.Class() not in ('BackdropNode',))
    branches = list(Branches(n)for n in nodes)
    branches.sort(key=len, reverse=True)

    last = None
    for i in branches:
        i.autoplace()
        if last:
            print(last.nodes.right)
            i.nodes.xpos = last.nodes.right + 20
        i.nodes.ypos = 0
        last = i
    for backdrop, nodes in backdrops_dict.items():
        if not nodes:
            continue
        nodes.autoplace()
        left, top, right, bottom = (-10, -80, 10, 10)
        xpos = nodes.xpos + left
        ypos = nodes.ypos + top
        width = nodes.width + (right - left)
        height = nodes.height + (bottom - top)
        backdrop.setXYpos(xpos, ypos)
        backdrop['bdwidth'].setValue(width)
        backdrop['bdheight'].setValue(height)
        # Move other nodes out.
        other_nodes = (n for n in nuke.allNodes()
                       if n not in nodes and n is not backdrop)
        for n in other_nodes:
            xpos = n.xpos()
            ypos = n.ypos()
            if nodes.xpos <= xpos <= nodes.right:
                ypos = ypos + bottom if ypos > nodes.ypos else ypos + top
            n.setXYpos(xpos, ypos)


def orgnize_nodes(nodes):
    """orgnize node posion and add backdrops.  """
    # TODO
    meta_input_dict = {}
    for n in nodes:
        meta_input = n.metadata('input/filename')
        if meta_input:
            meta_input_dict.setdefault(meta_input, [])
            meta_input_dict[meta_input].append(n)

    for meta_input, nodes in meta_input_dict.items():
        map(nuke.autoplace, nodes)
        n = create_backdrop(nodes)


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


# def autoplace(node):
#     """Autoplace given node."""
#     if node.Class() == 'BackdropNode':
#         autoplace_backdrop(node)
#     else:
#         autoplace_input(node)


class Nodes(list):
    """Geometry boder size of @nodes.  """
    y_gap = 10
    x_gap = 10

    def __init__(self, nodes=None):
        if nodes is None:
            nodes = []
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
        for n in self.outputs():
            branches = Branches(n, nodes=self)
            branches.autoplace()
        self.auto_margin()

    def outputs(self):
        """Return Nodes that has no contained downstream founded in given nodes.  """
        ret = (n for n in self if all(n not in self for n in n.dependent()))
        return ret

    def auto_margin(self):
        left_nodes = Nodes(n for n in nuke.allNodes()
                           if n not in self and n.xpos < self.xpos)
        if left_nodes:
            self.xpos = left_nodes.right + self.x_gap
        top_nodes = Nodes(n for n in nuke.allNodes()
                          if n not in self and n.ypos < self.ypos)
        if top_nodes:
            self.xpos = top_nodes.bottom + self.y_gap


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

    def __init__(self, node=None):
        self._origin = None
        self._origin_branch = None
        self._origin_nodes = []
        if isinstance(node, nuke.Node):
            node = [node]
        elif node is None:
            node = []
        Nodes.__init__(self, node)
        self._expanded = None

    def expand(self, nodes=None):
        """Expand self to upstream 1 time, can limit in @nodes.  """

        if self.expanded:
            return False
        ret = Branches()
        nodes = nodes or nuke.allNodes()
        end = self[-1]
        input_nodes = end.dependencies(nuke.INPUTS)
        for index, input_node in enumerate(input_nodes):
            if input_node not in nodes:
                continue
            if index == 0:
                branch = self
            else:
                branch = Branch()
                branch.origin = end
                branch._origin_nodes = list(self)
                branch._origin_branch = self
                branch.depth = self.depth + len(self)
            branch.append(input_node)
            ret.append(branch)
        return ret

    @property
    def expanded(self):
        """Return if this branch is expanded to end.  """
        if not self._expanded:
            origin = self[-1]
            input_nodes = origin.dependencies(nuke.INPUTS)
            self._expanded = not bool(input_nodes)
        return self._expanded

    def autoplace(self):
        """Autoplace nodes in this branch.  """
        ypos = self.ypos
        xpos = self.xpos
        for n in self[::-1]:
            n.setXYpos(xpos, ypos)
            ypos += n.screenHeight() + self.y_gap
        # Centerize
        width = self.width
        for n in self:
            xpos = n.xpos() + (width - n.screenWidth()) / 2
            n.setXpos(xpos)
        self.auto_margin()

    @property
    def origin(self):
        """The node branch expand from."""
        return self._origin

    @origin.setter
    def origin(self, value):
        if isinstance(value, nuke.Node):
            self._origin = value
        else:
            raise TypeError('Expected nuke.Node type.')

    @property
    def origin_nodes(self):
        """The nodes branch expand from."""
        return self._origin_nodes

    @property
    def origin_branch(self):
        """The branch this branch expand from."""
        return self._origin_branch

    def __str__(self):
        return 'Branch< {} >'.format(' -> '.join(n.name() for n in self))


class Branches(list):
    """A branches is a list of branch. (e.g. [branch1, branch2, ... branch_n]).  """

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
        """Expand all branched to the end.  """
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
                    self.insert(index, expanded[0])
                    for bran in expanded[1:]:

                        self.append(bran)
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

        self.sort(key=lambda x: x.depth, reverse=False)
        last = None
        for branch in self:
            branch.autoplace()
            branch.xpos = 0
            if last:
                branch.xpos = last.right + branch.x_gap
            branch.ypos = 0

            if branch.origin:
                branch.bottom = branch.origin.ypos() - branch.y_gap
                # nodes = Nodes(set(branch.origin_branch).difference(
                #     set(branch.origin_nodes)))
                # if nodes:
                #     nodes.ypos -= branch.height
            last = branch

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
        # autoplace(nodes)
        pass
    if not nodes:
        return nuke.nodes.BackdropNode()

    # Calculate bounds for the backdrop node.
    bdX = min([node.xpos() for node in nodes])
    bdY = min([node.ypos() for node in nodes])
    bdW = max([node.xpos() + node.screenWidth() for node in nodes]) - bdX
    bdH = max([node.ypos() + node.screenHeight() for node in nodes]) - bdY

    zOrder = 0
    selectedBackdropNodes = nuke.selectedNodes("BackdropNode")
    # if there are backdropNodes selected put the new one immediately behind the farthest one
    if len(selectedBackdropNodes):
        zOrder = min([node.knob("z_order").value()
                      for node in selectedBackdropNodes]) - 1
    else:
        # otherwise (no backdrop in selection) find the nearest backdrop if exists and set the new one in front of it
        nonSelectedBackdropNodes = nuke.allNodes("BackdropNode")
    for nonBackdrop in nodes:
        for backdrop in nonSelectedBackdropNodes:
            if is_node_inside(nonBackdrop, backdrop):
                zOrder = max(zOrder, backdrop.knob("z_order").value() + 1)

    # Expand the bounds to leave a little border. Elements are offsets for left, top, right and bottom edges respectively
    left, top, right, bottom = (-10, -80, 10, 10)
    bdX += left
    bdY += top
    bdW += (right - left)
    bdH += (bottom - top)

    n = nuke.nodes.BackdropNode(xpos=bdX,
                                bdwidth=bdW,
                                ypos=bdY,
                                bdheight=bdH,
                                tile_color=int(
                                    (random.random() * (16 - 10))) + 10,
                                note_font_size=42,
                                z_order=zOrder)

    return n
