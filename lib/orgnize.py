# -*- coding=UTF-8 -*-
"""Orgnize nodes layout.  """

import logging
import random
import sys
import time
import traceback

import nuke

from wlf.decorators import run_async
from wlf.notify import CancelledError, Progress

from edit import run_in_main_thread, undoable_func
from node import get_upstream_nodes

__version__ = '0.7.6'

LOGGER = logging.getLogger('com.wlf.orgnize')
DEBUG = False


def autoplace(nodes=None, recursive=False, undoable=True):
    """Auto place nodes."""

    if undoable:
        return undoable_func('自动摆放')(autoplace)(nodes, recursive, undoable=False)

    start = time.clock()
    nodes = nodes or nuke.allNodes()
    if not nodes:
        return
    elif isinstance(nodes, nuke.Node):
        nodes = [nodes]
    if recursive:
        nodes = get_upstream_nodes(nodes).union(nodes)

    nodes = Nodes(nodes)

    try:
        nodes.autoplace()
        LOGGER.debug(u'自动摆放耗时: %0.2f秒', time.clock() - start)
    except CancelledError:
        nuke.Undo.cancel()
    except:
        traceback.print_exc()
        nuke.Undo.end()
        raise


if nuke.GUI:
    setattr(sys.modules[__name__], 'autoplace', run_async(autoplace))


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

        Worker(self).autoplace()

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

    x_gap = 10
    y_gap = 10
    min_height = 22
    min_width = 60
    branch_thershold = 20
    non_base_node_classes = ('Viewer',)
    executing = False

    def __init__(self, nodes=None):
        self.nodes = nodes or nuke.allNodes()
        self.nodes = Nodes(self.nodes)
        self.end_nodes = set(self.nodes)
        self.base_node_dict = {}
        self.placed_nodes = set()
        self.counted_nodes = set()
        self.upstream_counts = {}
        self.prev_nodes = set()
        self.prev_branch_nodes = set()
        self.task = Progress('摆放节点', len(self.nodes))

        self.count()

    @run_in_main_thread
    def count(self):
        """Count @nodes upstream. recorded in self.upstream_counts.  """

        self.counted_nodes.clear()
        nodes = sorted(self.nodes, key=self.get_count, reverse=True)
        self.upstream_counts.clear()

        for n in nodes:
            self.get_count(n, True)

    def get_count(self, node, distinct=False):
        """Get upstream nodes count for @node.  """

        assert isinstance(node, nuke.Node),\
            'Expect a nuke.Node Type, got {}.'.format(repr(node))
        ret = 0
        counts_dict = self.upstream_counts
        if counts_dict.has_key(node):
            return counts_dict[node]

        for n in node.dependencies(nuke.INPUTS):
            if n not in self.nodes:
                continue
            ret += 1
            if node.Class() not in self.non_base_node_classes \
                    and (not distinct or n not in self.counted_nodes):
                ret += self.get_count(n, distinct)
                self.end_nodes.discard(n)

        if DEBUG:
            node['label'].setValue(str(ret))

        counts_dict[node] = ret
        if distinct:
            self.counted_nodes.add(node)
        return ret

    def autoplace(self):
        """Autoplace nodes.  """

        if Worker.executing and not run_in_main_thread(nuke.ask)('你确定要同时进行两个自动摆放?'):
            return
        Worker.executing = True

        backdrops_dict = {n: Nodes(n.getNodes())
                          for n in self.nodes if n.Class() == 'BackdropNode'}

        for n in sorted(self.end_nodes, key=self.get_count, reverse=True):
            assert isinstance(n, nuke.Node)
            self.autoplace_from(n)

        left, top, right, bottom = (-10, -80, 10, 10)
        for backdrop, nodes_in_backdrop in backdrops_dict.items():
            if not nodes_in_backdrop:
                continue
            up_nodes = Nodes(n for n in get_upstream_nodes(nodes_in_backdrop)
                             if n.ypos() < nodes_in_backdrop.bottom
                             and n not in nodes_in_backdrop)
            if up_nodes:
                up_nodes.bottom = nodes_in_backdrop.ypos + top - bottom
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

        Worker.executing = False

    def autoplace_from(self, node):
        """Autoplace @node and it's upstream.  """

        assert isinstance(node, nuke.Node)
        if node in self.placed_nodes:
            LOGGER.debug('Ignored placed node: %s', repr(node))
            return
        LOGGER.debug('Analysing node: %s', repr(node))
        base_node = self.get_base_node(node)
        is_new_branch = self.get_count(
            node) > self.branch_thershold

        # Place self
        LOGGER.debug('Placing node: %s', repr(node))
        if base_node:
            LOGGER.debug('Base: %s', repr(base_node))
            assert isinstance(base_node, nuke.Node)
            base_dep = base_node.dependencies()
            self_index = base_dep.index(node)
            xpos = base_node.xpos() + base_node.screenWidth() / 2 - node.screenWidth() / 2
            ypos = base_node.ypos() - self.y_gap - node.screenHeight()
            if self_index == 0:
                pass
            elif is_new_branch and self.placed_nodes:
                xpos = Nodes(self.placed_nodes).right + self.x_gap * 50
            else:
                prev_node = base_dep[self_index - 1]
                xpos = prev_node.xpos() + int(1.5 * max(prev_node.screenWidth(), self.min_width))  \
                    - node.screenWidth() / 2 + self.x_gap

            if not is_new_branch and base_node:
                # Replace prev nodes
                prev_nodes = Nodes(self.get_prev_nodes(node))
                if prev_nodes:
                    prev_nodes.bottom = min(
                        ypos - self.y_gap, prev_nodes.bottom)
        elif self.placed_nodes:
            xpos = Nodes(self.placed_nodes).right + self.x_gap * 10
            ypos = 0
        elif self.nodes == nuke.allNodes():
            xpos = 0
            ypos = 0
        else:
            xpos = self.nodes.xpos
            ypos = self.nodes.bottom - self.min_height

        LOGGER.debug('%s %s', xpos, ypos)
        node.setXYpos(xpos, ypos)
        if not base_node:
            self.prev_branch_nodes.update(self.placed_nodes)
        self.placed_nodes.add(node)
        self.task.step()

        if DEBUG:
            # node.selectOnly()
            nuke.zoomToFitSelected()
            if not nuke.ask('{}:\nbase:{}\nup count:{}\nx: {} y: {}\nnew_branch:{}'.format(
                    node.name(),
                    base_node and base_node.name(),
                    self.get_count(node),
                    xpos,
                    ypos,
                    is_new_branch)):
                raise RuntimeError

        if node.Class() not in self.non_base_node_classes:
            # Place upstream
            for n in node.dependencies(nuke.INPUTS):
                if n in self.nodes:
                    self.autoplace_from(n)

    @run_in_main_thread
    def get_base_node(self, node):
        """Get primary base node of @node.  """

        assert isinstance(node, nuke.Node)
        outcome_dict = self.base_node_dict
        if node in outcome_dict:
            return outcome_dict[node]

        downstream_nodes = node.dependent(nuke.INPUTS)
        downstream_nodes = downstream_nodes or []
        assert isinstance(downstream_nodes, list), downstream_nodes
        downstream_nodes = [i for i in downstream_nodes
                            if i.Class() not in self.non_base_node_classes]
        downstream_nodes.sort(
            key=lambda x: (x not in self.placed_nodes, self.get_count(x)))
        base_node = downstream_nodes[0] if downstream_nodes else None
        outcome_dict[node] = base_node

        LOGGER.debug('Base node for %s : %s', repr(node), repr(base_node))
        return base_node

    @run_in_main_thread
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
                if self.get_count(base) > self.branch_thershold:
                    break
                n = base
            else:
                break
        return ret

    @run_in_main_thread
    def get_prev_nodes(self, node):
        """Get previous placed nodes for @node.  """

        assert isinstance(node, nuke.Node)

        branch = self.get_branch(node)
        branch_base = self.get_base_node(branch[0])
        ret = set(self.placed_nodes)
        ret.difference_update(branch)
        ret.difference_update(self.prev_branch_nodes)
        if branch_base:
            ret.intersection_update(get_upstream_nodes(branch_base))

        return ret
