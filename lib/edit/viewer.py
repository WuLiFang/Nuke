# -*- coding=UTF-8 -*-
"""Viewer control.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Dict, Any


class CurrentViewer(object):
    """Manipulate currunt viewer."""

    def __init__(self):
        self.knob_values = {}  # type: Dict[nuke.Knob, Any]
        self.record()
        self.viewer = None
        self.node = None
        self.inputs = None

    def link(
        self,
        input_node,  # type: nuke.Node
        input_num=0,  # type: int
        replace=True,  # type: bool
    ):  # type: (...) -> None
        """Connet input_node to viewer.input0 then activate it,
        create viewer if needed."""

        if self.viewer:
            n = self.node
        else:
            viewers = nuke.allNodes(b"Viewer")
            if viewers:
                n = viewers[0]
            else:
                n = nuke.nodes.Viewer()
        self.node = n
        if not n:
            return
        if replace or not n.input(input_num):
            _ = n.setInput(input_num, input_node)
            try:
                nuke.activeViewer().activateInput(input_num)
            except AttributeError:
                pass

    def record(self):
        """Record current active viewer state."""

        self.viewer = nuke.activeViewer()
        if self.viewer:
            self.node = self.viewer.node()
            self.inputs = self.node.input(0)
            for knob in self.node.allKnobs():
                self.knob_values[knob] = knob.value()

    def recover(self):
        """Recover viewer state to last record."""

        if self.viewer:
            if self.node:
                _ = self.node.setInput(0, self.inputs)
            for knob, value in self.knob_values.items():
                try:
                    _ = knob.setValue(value)
                except TypeError:
                    pass
        elif self.node:
            nuke.delete(self.node)
