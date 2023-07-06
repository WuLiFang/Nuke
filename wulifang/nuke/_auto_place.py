# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none
# spell-checker: words autoplace bdwidth bdheight

from __future__ import absolute_import, division, print_function, unicode_literals


import threading

import nuke

from wulifang._util import (
    cast_str,
    cast_text,
    run_in_thread,
    run_in_main_thread,
    assert_isinstance,
)
from wulifang.nuke._util import (
    node_deep_dependencies,
    NodeList,
    knob_of,
)
import logging
import wulifang.nuke


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterable, Optional, Union

_LOCK = threading.Lock()
_DEBUG = False
_LOGGER = logging.getLogger(__name__)


def auto_place(
    nodes,  # type: Union[Iterable[nuke.Node], nuke.Node]
    recursive=False,  # type: bool
    async_=None,  # type: Optional[bool]
):  # type: (...) -> Union[None, threading.Thread]
    """Auto place nodes."""

    if async_ is None:
        async_ = _DEBUG

    # Executing check
    if not _LOCK.acquire(False):
        msg = "不能同时进行两个自动摆放"
        nuke.message(cast_str(msg))
        _LOGGER.warning(msg)
        return
    _LOCK.release()

    # Args check
    nodes = nuke.allNodes() if not nodes else nodes
    if not nodes:
        return
    elif async_ and nuke.GUI and not _DEBUG:
        return run_in_thread("auto-place", daemon=True)(auto_place)(
            nodes,
            recursive,
            async_=False,
        )

    # Call worker
    nodes = [nodes] if isinstance(nodes, nuke.Node) else nodes
    nodes = (
        node_deep_dependencies(nodes, flags=nuke.INPUTS).union(nodes)
        if recursive
        else nodes
    )
    nodes = NodeList(nodes)

    with _LOCK:
        try:
            manager = Manager(nodes)
            manager.auto_place()
        except:
            _LOGGER.exception(
                "Unexpected exception during auto place",
            )
            raise


class Analyser(object):
    """NodeList struct analyser."""

    non_base_node_classes = ("Viewer",)
    branch_threshold = 20

    def __init__(self, nodes):
        # type: (NodeList) -> None
        self.nodes = nodes
        self._end_nodes = set(self.nodes)
        self.base_node_dict = {}  # type: dict[nuke.Node, Optional[nuke.Node]]
        self.counted_nodes = set()  # type: set[nuke.Node]
        self.upstream_counts = {}  # type: dict[nuke.Node, int]

        _ = self.count()

    @run_in_main_thread
    def count(self):
        """Count @nodes upstream. recorded in self.upstream_counts."""

        self.counted_nodes.clear()
        nodes = sorted(self.nodes, key=self.get_count, reverse=True)
        self.upstream_counts.clear()

        for n in nodes:
            _ = self.get_count(n, True)

    @property
    def end_nodes(self):
        """NodeList that have no downstream node."""

        return sorted(self._end_nodes, key=self.get_count, reverse=True)

    def get_count(self, node, distinct=False):
        # type: (nuke.Node, bool) -> int
        """Get upstream nodes count for @node."""

        assert isinstance(node, nuke.Node), "Expect a nuke.Node Type, got {}.".format(
            repr(node)
        )

        ret = 0

        counts_dict = self.upstream_counts
        if node in counts_dict:
            return counts_dict[node]

        if isinstance(node, nuke.BackdropNode):
            _ = list(map(ret.__add__, [self.get_count(n) for n in node.getNodes()]))
        else:
            for n in node.dependencies(nuke.INPUTS):
                if n not in self.nodes:
                    continue
                ret += 1
                if cast_text(node.Class()) not in self.non_base_node_classes and (
                    not distinct or n not in self.counted_nodes
                ):
                    ret += self.get_count(n, distinct)
                    self._end_nodes.discard(n)

        if _DEBUG:
            knob_of(node, "label", nuke.String_Knob).setValue(cast_str(ret))

        counts_dict[node] = ret
        if distinct:
            self.counted_nodes.add(node)
        return ret


class Manager(Analyser):
    """Auto-place manager."""

    def __init__(self, nodes):
        # type: (NodeList) -> None
        super(Manager, self).__init__(nodes)

        self.nodes = nodes
        self.prev_nodes = set()  # type: set[nuke.Node]

    def auto_place(self):
        """Auto-place nodes."""

        backdrops = [n for n in self.nodes if isinstance(n, nuke.BackdropNode)]
        backdrops.sort(key=self.get_count)
        remains_nodes = set(self.nodes)

        # TODO

        # for backdrop in backdrops:
        #     assert isinstance(backdrop, nuke.BackdropNode)

        #     nodes = remains_nodes.intersection(backdrop.getNodeList())
        #     Worker(self, nodes, backdrop).run()
        #     remains_nodes.difference_update(backdrops)
        #     remains_nodes.difference_update(nodes)

        Worker(self, NodeList(remains_nodes)).run()

        nuke.Root().setModified(True)


class Worker(Analyser):
    """Auto-place worker."""

    x_gap = 10
    y_gap = 10
    min_height = 22
    min_width = 60

    class backdrop_padding:
        top = 80
        right = 10
        bottom = 10
        left = 10

    def __init__(self, manager, nodes, backdrop=None):
        # type: (Manager, NodeList, Optional[nuke.BackdropNode] ) -> None

        super(Worker, self).__init__(nodes)

        self.backdrop = backdrop
        self.nodes = nodes
        self.placed_nodes = set()  # type: set[nuke.Node]
        self.prev_branch_nodes = set()  # type: set[nuke.Node]

    def run(self):
        """Run this worker."""

        for n in self.end_nodes:
            self.auto_place_from(n)

        _ = self.auto_place_backdrop()

    def auto_place_from(self, node):
        # type: (nuke.Node) -> None
        """Auto-place @node and it's upstream."""

        assert isinstance(node, nuke.Node)

        _ = self.auto_place(node)

        if (
            cast_text(run_in_main_thread(node.Class)())
            not in self.non_base_node_classes
        ):
            for n in run_in_main_thread(node.dependencies)(nuke.INPUTS):
                if n in self.nodes and n not in self.placed_nodes:
                    self.auto_place_from(n)

    @run_in_main_thread
    def auto_place_backdrop(self):
        """Match backdrop size and position to nodes."""

        if not self.backdrop:
            return
        nodes = NodeList(self.nodes)
        backdrop = assert_isinstance(self.backdrop, nuke.BackdropNode)
        p = self.backdrop_padding

        if nodes:
            backdrop.setXYpos(nodes.xpos - p.left, nodes.ypos - p.top)
            knob_of(backdrop, "bdwidth", nuke.Array_Knob).setValue(
                nodes.width + p.right + p.left
            )
            knob_of(backdrop, "bdheight", nuke.Array_Knob).setValue(
                nodes.height + p.bottom + p.top
            )
        else:
            self.auto_place(backdrop)

    @run_in_main_thread
    def auto_place(self, node):
        # type: (nuke.Node) -> None
        """Auto-place single node."""

        def _base_node():
            # type: () -> Optional[tuple[int, int]]
            if base_node and base_node in self.nodes:
                assert isinstance(base_node, nuke.Node)
                base_dep = base_node.dependencies(nuke.INPUTS)
                self_index = base_dep.index(node)
                is_new_branch = self.is_new_branch(node)
                xpos = int(
                    base_node.xpos()
                    + base_node.screenWidth() / 2
                    - node.screenWidth() / 2
                )
                ypos = (
                    base_node.ypos()
                    - self.y_gap
                    - max(node.screenHeight(), self.min_height)
                )
                if self_index == 0:
                    pass
                elif is_new_branch and self.placed_nodes:
                    xpos = NodeList(self.placed_nodes).right + self.x_gap
                else:
                    prev_node = base_dep[self_index - 1]
                    xpos = int(
                        prev_node.xpos()
                        + int(1.5 * max(prev_node.screenWidth(), self.min_width))
                        - node.screenWidth() / 2
                        + self.x_gap
                    )

                if not is_new_branch:
                    # Replace prev nodes
                    prev_nodes = NodeList(self.get_prev_nodes(node))
                    if prev_nodes:
                        prev_nodes.bottom = min(ypos - self.y_gap, prev_nodes.bottom)
                return (xpos, ypos)

        def _backdrop():
            # type: () -> Optional[tuple[int, int]]
            backdrop = self.backdrop
            padding = self.backdrop_padding

            if backdrop:
                assert isinstance(backdrop, nuke.Node)

                backdrop = NodeList([backdrop])
                xpos = backdrop.xpos + padding.left
                ypos = backdrop.bottom - padding.bottom - node.screenHeight()
                return (xpos, ypos)

        def _placed_nodes():
            # type: () -> Optional[tuple[int, int]]
            if self.placed_nodes:
                nodes = NodeList(self.placed_nodes)
                xpos = nodes.right + self.x_gap * 10
                ypos = -node.screenHeight()
                return (xpos, ypos)

        def _all_nodes():
            # type: () -> Optional[tuple[int, int]]
            if not set(nuke.allNodes()).difference(self.nodes):
                xpos = 0
                ypos = -node.screenHeight()
                return (xpos, ypos)

        def _default():
            # type: () -> tuple[int, int]
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
            raise RuntimeError("No auto-place method can be used.")

        if not base_node:
            self.prev_branch_nodes.update(self.placed_nodes)
        self.placed_nodes.add(node)

        if _DEBUG:
            # node.selectOnly()
            nuke.zoomToFitSelected()
            if not nuke.ask(
                cast_str(
                    "{}:\nbase:{}\nup count:{}\nmethod:{}\nx: {} y: {}".format(
                        self.get_count(node), method.__name__, *pos
                    )
                )
            ):
                raise RuntimeError

    @run_in_main_thread
    def get_base_node(self, node):
        # type: (nuke.Node) -> Optional[nuke.Node]
        """Get primary base node of @node."""

        outcome_dict = self.base_node_dict
        if node in outcome_dict:
            return outcome_dict[node]

        downstream_nodes = node.dependent(nuke.INPUTS, False)
        assert isinstance(downstream_nodes, list), downstream_nodes
        downstream_nodes = [
            i
            for i in downstream_nodes
            if cast_text(i.Class()) not in self.non_base_node_classes
        ]
        downstream_nodes.sort(
            key=lambda x: (x not in self.placed_nodes, self.get_count(x))
        )
        base_node = downstream_nodes[0] if downstream_nodes else None

        outcome_dict[node] = base_node

        return base_node

    @run_in_main_thread
    def get_prev_nodes(self, node):
        # type: (nuke.Node) -> set[nuke.Node]
        """Get previous placed nodes for @node."""

        assert isinstance(node, nuke.Node)

        branch = self.get_branch(node)
        branch_base = self.get_base_node(branch[0])
        ret = set(self.placed_nodes)
        if branch_base:
            ret.intersection_update(
                node_deep_dependencies(branch_base, flags=nuke.INPUTS)
            )
        ret.difference_update(branch)
        ret.difference_update(self.prev_branch_nodes)

        return ret

    @run_in_main_thread
    def is_new_branch(self, node, from_bottom=True):
        # type: (nuke.Node, bool) -> bool
        """Return if this @node starts a new branch."""

        return (
            not self.get_base_node(node)
            or self.get_count(node) > self.branch_threshold
            and (from_bottom or len(node.dependencies(nuke.INPUTS)) > 1)
        )

    @run_in_main_thread
    def get_branch(self, node):
        # type: (nuke.Node) -> list[nuke.Node]
        """Get primary branch of @node."""

        ret = []  # type: list[nuke.Node]
        n = node
        while True:
            if not n or self.is_new_branch(n, from_bottom=False):
                break
            ret.insert(0, n)
            base = self.get_base_node(n)
            n = base
        return ret


def _on_script_save():
    if (
        nuke.numvalue(cast_str("preferences.wlf_autoplace"), 0.0)
        and nuke.Root().modified()
    ):
        t = nuke.numvalue(cast_str("preferences.wlf_autoplace_type"), 0.0)
        _LOGGER.debug("Auto-place. type: %s", t)
        if t == 0.0:
            _ = auto_place(nuke.allNodes(), async_=False)
        else:
            for i in nuke.allNodes():
                nuke.autoplace(i)


def init_gui():
    wulifang.nuke.callback.on_script_save(_on_script_save)
