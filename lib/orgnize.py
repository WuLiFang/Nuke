# -*- coding=UTF-8 -*-
"""Orgnize nodes layout.  """
import random
import logging

import nuke

from wlf.notify import Progress, CancelledError

from node import get_upstream_nodes

__version__ = '0.6.1'

LOGGER = logging.getLogger('com.wlf.orgnize')
DEBUG = False


def autoplace(nodes=None, recursive=False):
    """Auto place nodes."""

    nodes = nodes or nuke.allNodes()
    if not nodes:
        return
    elif isinstance(nodes, nuke.Node):
        nodes = [nodes]
    if recursive:
        nodes = get_upstream_nodes(nodes).union(nodes)
    nodes = Nodes(nodes)

    xpos, bottom = nodes.xpos, nodes.bottom
    try:
        nodes.autoplace()
    except CancelledError:
        nuke.Undo.cancel()
        print('用户取消自动摆放')
        return
    if nodes != nuke.allNodes():
        nodes.xpos, nodes.bottom = xpos, bottom


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

        if not self:
            return
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
                up_nodes.bottom = nodes_in_backdrop.ypos + top - self.y_gap
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


class Branch(Nodes):
    """A branch is a list of connected nodes. (e.g. [node1, node2, ... node_n]).  """

    parent_branch = None
    base_node = None
    _expanded = None
    big_branch_thershold = 10

    def expand(self, nodes=None):
        """Expand self to upstream 1 time, can limit in @nodes.  """

        if self.expanded:
            return False
        ret = Branches()
        nodes = nodes or nuke.allNodes()
        base = self[-1]
        input_nodes = base.dependencies(nuke.INPUTS)
        for index, input_node in enumerate(input_nodes):
            if input_node not in nodes:
                continue
            if index == 0:
                branch = self
            else:
                branch = Branch()
                branch.parent_branch = self
                branch.base_node = base
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

    def dependent(self):
        """All nodes read information from this branch.  """

        ret = set()
        for n in self:
            ret.update(n.dependent(nuke.INPUTS))
        ret.difference_update(self)
        return ret

    def autoplace(self):
        """Autoplace nodes in this branch.  """

        nodes = Nodes(n for n in self if n not in Branches.placed_nodes)
        if not nodes:
            return
        if self.base_node:
            prev_nodes = Nodes(n for n in get_upstream_nodes(self.base_node)
                               if n in Branches.placed_nodes)
        else:
            prev_nodes = Nodes()
        dependencies = self.dependent()

        # nuke.zoomToFitSelected()
        # if not nuke.ask(self.base_node and self.base_node.name() or 'None'):
        #     raise RuntimeError

        # Y-axis.
        ypos = 0
        for n in nodes:
            ypos -= n.screenHeight() + self.y_gap
            n.setYpos(ypos)
        if self.base_node:
            # Place nodes accroding base.
            n = self.base_node
            while n:
                up_node = n.input(0)
                if up_node and up_node in dependencies:
                    n = up_node
                    prev_nodes.remove(n)
                else:
                    break
            nodes.bottom = n.ypos() - self.y_gap
        if len(nodes) < self.big_branch_thershold:
            # Move prev nodes up.
            if prev_nodes:
                prev_nodes.bottom = nodes.ypos - nodes.y_gap

        # X-axis.
        if len(nodes) >= self.big_branch_thershold and Branches.placed_nodes:
            xpos = Nodes(Branches.placed_nodes).right + self.x_gap * 50
        else:
            xpos = 0

        left_nodes = Nodes(n for n in prev_nodes
                           if n.ypos() >= nodes.ypos
                           and Nodes(n).bottom <= nodes.bottom)
        if left_nodes:
            xpos = max([left_nodes.right + self.x_gap, xpos])
        if self.base_node:
            xpos = max([Nodes(self.base_node).right + self.x_gap, xpos])

        for n in nodes:
            n.setXpos(xpos + (nodes.max_width - n.screenWidth()) / 2)

    def __str__(self):
        return '<Branch<{}>@{}>'.format(' -> '.join(n.name() for n in self),
                                        self.base_node and self.base_node.name())


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
        task = Progress('分析结构')
        count = 0
        while not_done:
            task.set(message='向上{}层节点'.format(count))
            count += 1
            not_done = False
            itering = list(self)
            del self[:]
            all_num = len(itering)
            for index, branch in enumerate(itering):
                if count >= 50:
                    task.set(index * 100 // all_num)
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
            assert isinstance(branch, Branch)
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


class Worker(object):
    """Autoplace worker"""

    y_gap = 10
    x_gap = 10
    min_height = 22
    min_width = 80
    branch_thershold = 20

    def __init__(self, nodes=None):
        self.nodes = nodes or nuke.allNodes()
        self.end_nodes = set(self.nodes)
        self.placed_nodes = set()
        self.counted_nodes = set()
        self.upstream_counts = {}
        self.prev_nodes = set()

        self.count(self.nodes, False)
        self.count(self.end_nodes, True)

    def count(self, nodes, distinct=True):
        """Count @nodes upstream. recorded in self.upstream_counts.  """

        self.upstream_counts.clear()
        self.counted_nodes.clear()
        for n in list(nodes):
            self.get_count(n, distinct)

    def get_count(self, node, distinct=True):
        """Get upstream nodes count for @node.  """

        assert isinstance(node, nuke.Node), 'Expect a nuke.Node Type.'
        ret = 0
        counts_dict = self.upstream_counts
        if counts_dict.has_key(node):
            return counts_dict[node]

        for n in node.dependencies(nuke.INPUTS):
            if n not in self.nodes:
                continue
            ret += 1
            if node.Class() not in ('Viewer',)\
                    and (not distinct or n not in self.counted_nodes):
                ret += self.get_count(n)
                self.end_nodes.discard(n)

        if DEBUG:
            node['label'].setValue(str(ret))

        counts_dict[node] = ret
        self.counted_nodes.add(node)
        return ret

    def autoplace(self):
        """Autoplace nodes.  """

        for n in sorted(self.end_nodes, key=self.get_count, reverse=True):
            assert isinstance(n, nuke.Node)
            self.autoplace_from(n)

        nuke.Root().setModified(True)

    def autoplace_from(self, node):
        """Autoplace @node and it's upstream.  """

        assert isinstance(node, nuke.Node)
        if node in self.placed_nodes:
            LOGGER.warning('Ignored placed node: %s', repr(node))
            return
        LOGGER.debug('Place node: %s', repr(node))
        base_node = self.get_base_node(node)
        is_new_branch = self.get_count(node) > self.branch_thershold

        # Place self
        if self.placed_nodes:
            xpos = Nodes(self.placed_nodes).right + self.x_gap
        else:
            xpos = 0
        ypos = 0
        if base_node:
            LOGGER.debug('Base: %s', repr(base_node))
            assert isinstance(base_node, nuke.Node)
            base_dep = base_node.dependencies()
            self_index = base_dep.index(node)
            xpos = base_node.xpos()
            ypos = base_node.ypos() - self.y_gap - node.screenHeight()
            if self_index == 0:
                pass
            elif is_new_branch:
                xpos += self.x_gap * 50
            else:
                prev_node = base_dep[self_index - 1]
                xpos = prev_node.xpos() + prev_node.screenWidth() + self.x_gap

            if not is_new_branch:
                # Replace prev nodes
                prev_nodes = Nodes(self.get_prev_nodes(node))
                if prev_nodes:
                    prev_nodes.bottom = min(
                        ypos - self.y_gap, prev_nodes.bottom)

        LOGGER.debug('%s %s', xpos, ypos)
        node.setXYpos(xpos, ypos)
        self.placed_nodes.add(node)
        self.prev_nodes.add(node)

        if DEBUG:
            nuke.zoomToFitSelected()
            if not nuke.ask('{}:\nbase:{}\nup count:{}\nx: {} y: {}\nnew_branch:{}'.format(
                    node.name(),
                    base_node and base_node.name(),
                    self.get_count(node),
                    xpos,
                    ypos,
                    is_new_branch)):
                raise RuntimeError

        # Place upstream
        for n in node.dependencies():
            if n in self.nodes:
                self.autoplace_from(n)

    def get_base_node(self, node):
        """Get primary base node of @node.  """

        assert isinstance(node, nuke.Node)
        downstream_nodes = sorted(
            node.dependent(nuke.INPUTS),
            key=lambda x: (x not in self.placed_nodes, self.upstream_counts[x]))
        base_node = (downstream_nodes and downstream_nodes[0]) or None

        return base_node

    def get_branch(self, node):
        """Get primary branch of @node.  """

        assert isinstance(node, nuke.Node)

        ret = [node]
        n = node
        while True:
            base = self.get_base_node(n)
            if base:
                assert isinstance(base, nuke.Node)
                ret.insert(0, base)
                if base.dependencies(nuke.INPUTS).index(n) != 0\
                        or self.get_count(base) > self.branch_thershold:
                    break
                n = base
            else:
                break
        return ret

    def get_prev_nodes(self, node):
        """Get previous placed nodes for @node.  """

        assert isinstance(node, nuke.Node)

        branch = self.get_branch(node)
        branch_base = self.get_base_node(branch[0])
        ret = set(self.placed_nodes)
        ret.difference_update(branch)
        if branch_base:
            ret.intersection_update(get_upstream_nodes(branch_base))

        return ret
