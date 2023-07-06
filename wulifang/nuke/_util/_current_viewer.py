# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang._util import cast_str, cast_text, assert_not_none
from ._is_node_deleted import is_node_deleted
from ._try_apply_knob_values import try_apply_knob_values

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Optional


class CurrentViewer:
    """Manipulate current viewer."""

    def __init__(self):
        self._recover = lambda: None

    @classmethod
    def obtain(cls):
        # type: () -> nuke.ViewerWindow

        viewer = nuke.activeViewer()
        if viewer:
            return viewer
        if not nuke.allNodes(cast_str("Viewer")):
            nuke.createNode(cast_str("Viewer"))
        return assert_not_none(nuke.activeViewer())

    @classmethod
    def show(
        cls,
        input_node,  # type: nuke.Node
        input_num=0,  # type: int
    ):  # type: (...) -> None
        """
        Connect input_node to viewer.input then activate it,
        create viewer if needed.
        """

        n = cls.obtain().node()
        n.setInput(input_num, input_node)
        try:
            assert_not_none(nuke.activeViewer()).activateInput(input_num)
        except AssertionError:
            pass

    def record(self):
        """Record current active viewer state."""

        viewer = nuke.activeViewer()
        if not viewer:
            self._recover = lambda: None
            return
        n = viewer.node()
        active_input = viewer.activeInput() or 0
        active_input_node = n.input(active_input)
        knob_values = {cast_text(k.name()): k.value() for k in n.allKnobs()}

        def recover():
            if is_node_deleted(n):
                return
            n.setInput(active_input, active_input_node)
            try_apply_knob_values(n, knob_values)

        self._recover = recover

    def recover(self):
        """Recover viewer state to last record."""

        self._recover()

    def __enter__(self):
        self.record()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # type: (Optional[type], Optional[Exception], Optional[object]) -> bool

        self.recover()
        return False
