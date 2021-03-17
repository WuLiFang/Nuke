# -*- coding=UTF-8 -*-
"""Orgnize nodes layout.  """
from __future__ import absolute_import, print_function

import logging
import os
import random
import threading
from collections import Iterable, namedtuple

import cast_unknown as cast
import nuke

import callback
from nodeutil import Nodes, get_upstream_nodes
from nuketools import undoable_func
from wlf.decorators import run_async, run_in_main_thread, run_with_clock

LOGGER = logging.getLogger('com.wlf.orgnize')
assert isinstance(LOGGER, logging.Logger)
DEBUG = False
LOCK = threading.Lock()


def autoplace(nodes=None, recursive=False, undoable=True, async_=None):
    """Auto place nodes."""

    if async_ is None:
        async_ = DEBUG

    # Executing check
    if not LOCK.acquire(False):
        msg = u'不能同时进行两个自动摆放'
        nuke.message(cast.binary(msg))
        LOGGER.warning(msg)
        return
    LOCK.release()

    # Args check
    nodes = nuke.allNodes() if not nodes else nodes
    if not nodes:
        return
    elif async_ and nuke.GUI and not DEBUG:
        return run_async(autoplace)(nodes, recursive, undoable, async_=False)

    # Call worker
    nodes = [nodes] if isinstance(nodes, nuke.Node) else nodes
    nodes = get_upstream_nodes(nodes, flags=nuke.INPUTS).union(
        nodes) if recursive else nodes
    nodes = Nodes(nodes)

    with LOCK:
        try:
            manager = Manager(nodes)
            manager.autoplace()
        except:
            LOGGER.error(
                'Unexcepted excepitoion during autoplace.', exc_info=True)
            raise


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


def rename_all_nodes():
    """Rename all nodes by them belonged backdrop node ."""

    for i in nuke.allNodes('BackdropNode'):
        _nodes = i.getNodes()
        j = i['label'].value().split('\n')[0].split(' ')[0]
        for k in _nodes:
            if k.Class() == 'Group' and not '_' in k.name() and not (k['disable'].value()):
                name = k.name().rstrip('0123456789')
                k.setName(name + '_' + j + '_1', updateExpressions=True)
            elif not ('_' in k.name()
                      or nuke.exists(k.name() + '.disable')
                      or (k['disable'].value())):
                k.setName(k.Class() + '_' + j + '_1', updateExpressions=True)


def split_by_backdrop():
    # TODO: need refactor and test.
    """Split workfile to multiple file by backdrop."""

    text_saveto = '保存至:'
    text_ask_if_create_new_folder = '目标文件夹不存在, 是否创建?'

    # Panel
    panel = nuke.Panel('splitByBackdrop')
    panel.addFilenameSearch(text_saveto, os.getenv('TEMP'))
    panel.show()

    # Save splited .nk file
    save_path = panel.value(text_saveto).rstrip('\\/')
    noname_count = 0
    for i in nuke.allNodes('BackdropNode'):
        label = repr(i['label'].value()).strip(
            "'").replace('\\', '_').replace('/', '_')
        if not label:
            noname_count += 1
            label = 'noname_{0:03d}'.format(noname_count)
        if not os.path.exists(save_path):
            if not nuke.ask(text_ask_if_create_new_folder):
                return False
        dir_ = save_path + '/splitnk/'
        dir_ = os.path.normcase(dir_)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        filename = dir_ + label + '.nk'
        i.selectOnly()
        i.selectNodes()
        nuke.nodeCopy(filename)
    os.system('explorer "' + dir_ + '"')
    return True


def nodes_add_dots(nodes=None):
    """Add dots to orgnize node tree."""

    if not nodes:
        nodes = nuke.selectedNodes()

    def _add_dot(output_node, input_num):
        input_node = output_node.input(input_num)
        if not input_node\
                or input_node.Class() in ['Dot']\
                or abs(output_node.xpos() - input_node.xpos()) < output_node.screenWidth()\
                or abs(output_node.ypos() - input_node.ypos()) <= output_node.screenHeight():
            return None
        if output_node.Class() in ['Viewer'] or output_node['hide_input'].value():
            return None

        _dot = nuke.nodes.Dot(inputs=[input_node])
        output_node.setInput(input_num, _dot)
        _dot.setXYpos(
            input_node.xpos() + input_node.screenWidth() / 2 - _dot.screenWidth() / 2,
            output_node.ypos() + output_node.screenHeight() / 2 - _dot.screenHeight() /
            2 - (_dot.screenHeight() + 5) * input_num
        )

    def _all_input_add_dot(node):
        for input_num in range(node.inputs()):
            _add_dot(node, input_num)

    for n in nodes:
        if n.Class() in ['Dot']:
            continue
        _all_input_add_dot(n)


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


class Analyser(object):
    """Nodes stuct analyser.  """

    non_base_node_classes = ('Viewer',)
    branch_thershold = 20

    def __init__(self, nodes):
        self.nodes = nodes
        self._end_nodes = set(self.nodes)
        self.base_node_dict = {}
        self.counted_nodes = set()
        self.upstream_counts = {}

        self.count()

    @run_in_main_thread
    def count(self):
        """Count @nodes upstream. recorded in self.upstream_counts.  """

        self.counted_nodes.clear()
        nodes = sorted(self.nodes, key=self.get_count, reverse=True)
        self.upstream_counts.clear()

        for n in nodes:
            self.get_count(n, True)

    @property
    def end_nodes(self):
        """Nodes that have no downstream node.  """

        return sorted(self._end_nodes, key=self.get_count, reverse=True)

    def get_count(self, node, distinct=False):
        """Get upstream nodes count for @node.  """

        assert isinstance(node, nuke.Node),\
            'Expect a nuke.Node Type, got {}.'.format(repr(node))

        ret = 0

        counts_dict = self.upstream_counts
        if counts_dict.has_key(node):
            return counts_dict[node]

        if isinstance(node, nuke.BackdropNode):
            map(ret.__add__, [self.get_count(n) for n in node.getNodes()])
        else:
            for n in node.dependencies(nuke.INPUTS):
                if n not in self.nodes:
                    continue
                ret += 1
                if node.Class() not in self.non_base_node_classes \
                        and (not distinct or n not in self.counted_nodes):
                    ret += self.get_count(n, distinct)
                    self._end_nodes.discard(n)

        if DEBUG:
            node['label'].setValue(str(ret))

        counts_dict[node] = ret
        if distinct:
            self.counted_nodes.add(node)
        return ret


class Manager(Analyser):
    """Autoplace manager.  """

    def __init__(self, nodes):
        assert isinstance(nodes, Iterable)

        nodes = Nodes(nodes)
        super(Manager, self).__init__(nodes)

        self.nodes = nodes
        self.prev_nodes = set()

    @run_with_clock(u'自动摆放')
    @undoable_func(u'自动摆放')
    def autoplace(self):
        """Autoplace nodes.  """

        backdrops = [n for n in self.nodes if isinstance(n, nuke.BackdropNode)]
        backdrops.sort(self.get_count)
        remains_nodes = set(self.nodes)

        # TODO

        # for backdrop in backdrops:
        #     assert isinstance(backdrop, nuke.BackdropNode)

        #     nodes = remains_nodes.intersection(backdrop.getNodes())
        #     Worker(self, nodes, backdrop).run()
        #     remains_nodes.difference_update(backdrops)
        #     remains_nodes.difference_update(nodes)

        Worker(self, remains_nodes).run()

        nuke.Root().setModified(True)


class Worker(Analyser):
    """Autoplace worker.  """

    x_gap = 10
    y_gap = 10
    min_height = 22
    min_width = 60
    Padding = namedtuple('Padding', 'top right bottom left')
    backdrop_padding = Padding(80, 10, 10, 10)

    def __init__(self, manager, nodes, backdrop=None):
        assert isinstance(manager, Manager)
        assert isinstance(nodes, Iterable), nodes
        assert backdrop is None \
            or isinstance(backdrop, nuke.BackdropNode)

        super(Worker, self).__init__(nodes)

        nodes = Nodes(nodes)

        self.backdrop = backdrop
        self.nodes = nodes
        self.placed_nodes = set()
        self.prev_branch_nodes = set()

    def run(self):
        """Run this worker.  """

        for n in self.end_nodes:
            self.autoplace_from(n)

        self.autoplace_backdrop()

    def autoplace_from(self, node):
        """Autoplace @node and it's upstream.  """

        assert isinstance(node, nuke.Node)
        rim = run_in_main_thread

        self.autoplace(node)

        if rim(node.Class)() not in self.non_base_node_classes:
            for n in rim(node.dependencies)(nuke.INPUTS) or tuple():
                if n in self.nodes and n not in self.placed_nodes:
                    self.autoplace_from(n)

    @run_in_main_thread
    def autoplace_backdrop(self):
        """Match backdrop size and position to nodes.   """

        nodes = Nodes(self.nodes)
        backdrop = self.backdrop
        top, right, bottom, left = self.backdrop_padding

        if not backdrop:
            pass
        elif nodes:
            backdrop.setXYpos(nodes.xpos - left, nodes.ypos - top)
            backdrop['bdwidth'].setValue(nodes.width + right + left)
            backdrop['bdheight'].setValue(nodes.height + bottom + top)
        else:
            self.autoplace(backdrop)

    @run_in_main_thread
    def autoplace(self, node):
        """Autoplace single node.  """

        def _base_node():
            if base_node and base_node in self.nodes:
                assert isinstance(base_node, nuke.Node)
                base_dep = base_node.dependencies(nuke.INPUTS)
                self_index = base_dep.index(node)
                is_new_branch = self.is_new_branch(node)
                xpos = base_node.xpos() + base_node.screenWidth() / 2 - node.screenWidth() / 2
                ypos = base_node.ypos() - self.y_gap - max(node.screenHeight(), self.min_height)
                if self_index == 0:
                    pass
                elif is_new_branch and self.placed_nodes:
                    xpos = Nodes(self.placed_nodes).right + self.x_gap * 50
                else:
                    prev_node = base_dep[self_index - 1]
                    xpos = prev_node.xpos()\
                        + int(1.5 * max(prev_node.screenWidth(), self.min_width))  \
                        - node.screenWidth() / 2 + self.x_gap

                if not is_new_branch:
                    # Replace prev nodes
                    prev_nodes = Nodes(self.get_prev_nodes(node))
                    if prev_nodes:
                        prev_nodes.bottom = min(
                            ypos - self.y_gap, prev_nodes.bottom)
                return (xpos, ypos)

        def _backdrop():
            backdrop = self.backdrop
            padding = self.backdrop_padding

            if backdrop:
                assert isinstance(backdrop, nuke.Node)

                backdrop = Nodes(backdrop)
                xpos = backdrop.xpos + padding.left
                ypos = backdrop.bottom - padding.bottom - node.screenHeight()
                return (xpos, ypos)

        def _placed_nodes():
            if self.placed_nodes:
                nodes = Nodes(self.placed_nodes)
                xpos = nodes.right + self.x_gap * 10
                ypos = -node.screenHeight()
                return (xpos, ypos)

        def _all_nodes():
            if not set(nuke.allNodes()).difference(self.nodes):
                xpos = 0
                ypos = -node.screenHeight()
                return (xpos, ypos)

        def _default():
            xpos = self.nodes.xpos
            ypos = self.nodes.bottom - self.min_height
            return (xpos, ypos)

        base_node = self.get_base_node(node)
        methods = (_base_node, _backdrop, _placed_nodes, _all_nodes, _default)
        pos = None
        method = None
        for method in methods:
            pos = method()
            if pos:
                node.setXYpos(*pos)
                break
        else:
            raise RuntimeError('No autoplace method can be used.')

        if not base_node:
            self.prev_branch_nodes.update(self.placed_nodes)
        self.placed_nodes.add(node)

        if DEBUG:
            # node.selectOnly()
            nuke.zoomToFitSelected()
            if not nuke.ask('{}:\nbase:{}\nup count:{}\nmethod:{}\nx: {} y: {}'.format(
                    self.get_count(node),
                    method.__name__,
                    *pos)):
                raise RuntimeError

    @run_in_main_thread
    def get_base_node(self, node):
        """Get primary base node of @node.  """

        assert isinstance(node, nuke.Node)
        outcome_dict = self.base_node_dict
        if node in outcome_dict:
            return outcome_dict[node]

        downstream_nodes = node.dependent(nuke.INPUTS, False)
        assert isinstance(downstream_nodes, list), downstream_nodes
        downstream_nodes = [i for i in downstream_nodes
                            if i.Class() not in self.non_base_node_classes]
        downstream_nodes.sort(key=lambda x: (
            x not in self.placed_nodes, self.get_count(x)))
        base_node = downstream_nodes[0] if downstream_nodes else None

        outcome_dict[node] = base_node

        return base_node

    @run_in_main_thread
    def get_prev_nodes(self, node):
        """Get previous placed nodes for @node.  """

        assert isinstance(node, nuke.Node)

        branch = self.get_branch(node)
        branch_base = self.get_base_node(branch[0])
        ret = set(self.placed_nodes)
        if branch_base:
            ret.intersection_update(get_upstream_nodes(
                branch_base, flags=nuke.INPUTS))
        ret.difference_update(branch)
        ret.difference_update(self.prev_branch_nodes)

        return ret

    @run_in_main_thread
    def is_new_branch(self, node, from_bottom=True):
        """Return if this @node starts a new branch.  """

        assert isinstance(node, nuke.Node)
        return not self.get_base_node(node)\
            or self.get_count(node) > self.branch_thershold\
            and (from_bottom or len(node.dependencies(nuke.INPUTS)) > 1)

    @run_in_main_thread
    def get_branch(self, node):
        """Get primary branch of @node.  """

        assert isinstance(node, nuke.Node)

        ret = []
        n = node
        while True:
            if not n or self.is_new_branch(n, from_bottom=False):
                break
            ret.insert(0, n)
            base = self.get_base_node(n)
            n = base
        return ret


def _autoplace():
    if nuke.numvalue('preferences.wlf_autoplace', 0.0) and nuke.Root().modified():
        autoplace_type = nuke.numvalue('preferences.wlf_autoplace_type', 0.0)
        LOGGER.debug('Autoplace. type: %s', autoplace_type)
        if autoplace_type == 0.0:
            autoplace(async_=False)
        else:
            map(nuke.autoplace, nuke.allNodes())


def setup():
    callback.CALLBACKS_ON_SCRIPT_SAVE.append(_autoplace)
