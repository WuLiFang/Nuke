# -*- coding=UTF-8 -*-
"""Viewer control.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke


class CurrentViewer(object):
    """Manipulate currunt viewer."""

    viewer = None
    node = None
    inputs = None
    knob_values = None

    def __init__(self):
        self.knob_values = {}
        self.record()

    def link(self, input_node, input_num=0, replace=True):
        """Connet input_node to viewer.input0 then activate it,
            create viewer if needed."""

        if self.viewer:
            n = self.node
        else:
            viewers = nuke.allNodes('Viewer')
            if viewers:
                n = viewers[0]
            else:
                n = nuke.nodes.Viewer()
        self.node = n

        if replace or not n.input(input_num):
            n.setInput(input_num, input_node)
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
            self.node.setInput(
                0, self.inputs)
            for knob, value in self.knob_values.items():
                try:
                    knob.setValue(value)
                except TypeError:
                    pass
        else:
            nuke.delete(self.node)
