# -*- coding=UTF-8 -*-
"""Viewer control.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

TYPE_CHECKING = False
if TYPE_CHECKING:
    from .. import types


class ActiveViewerService(object):
    def _node(self):
        v = nuke.activeViewer()
        if v:
            return v.node()

    def set_input(self, node, index=0):
        # type: (nuke.Node, int) -> None
        n = self._node()
        if not n:
            return
        n.setInput(index, node)

    def set_default_input(self, node, index=0):
        # type: (nuke.Node, int) -> None
        n = self._node()
        if not n:
            return
        if n.input(index):
            return
        n.setInput(index, node)


def _(v):
    # type: (ActiveViewerService) -> types.ActiveViewerService
    return v
