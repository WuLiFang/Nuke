# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke


def gizmo_to_group(gizmo):
    # type: (nuke.Gizmo) -> nuke.Group
    """Convert given gizmo node to group node."""
    
    _selected = gizmo[b"selected"].value()
    _group = gizmo.makeGroup()

    # Set Input.
    for i in range(gizmo.inputs()):
        _ = _group.setInput(i, gizmo.input(i))
    # Set Output.
    for n in nuke.allNodes():
        for i in range(n.inputs()):
            if n.input(i) is gizmo:
                _ = n.setInput(i, _group)

    # Set position and name.
    if gizmo.shown():
        _group.showControlPanel()
    _group.setXYpos(gizmo.xpos(), gizmo.ypos())
    _name = gizmo[b"name"].value()
    nuke.delete(gizmo)
    _group.setName(_name)
    _ = _group[b"selected"].setValue(_selected)

    return _group
