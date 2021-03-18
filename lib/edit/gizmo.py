# -*- coding=UTF-8 -*-
"""Convert nuke gizmo.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke


def gizmo_to_group(gizmo):
    """Convert given gizmo node to group node."""

    if not isinstance(gizmo, nuke.Gizmo):
        return gizmo

    _selected = gizmo['selected'].value()
    _group = gizmo.makeGroup()

    # Set Input.
    for i in range(gizmo.inputs()):
        _group.setInput(i, gizmo.input(i))
    # Set Output.
    for n in nuke.allNodes():
        for i in range(n.inputs()):
            if n.input(i) is gizmo:
                n.setInput(i, _group)

    # Set position and name.
    if gizmo.shown():
        _group.showControlPanel()
    _group.setXYpos(gizmo.xpos(), gizmo.ypos())
    _name = gizmo['name'].value()
    nuke.delete(gizmo)
    _group.setName(_name)
    _group[b'selected'].setValue(_selected)

    return _group


def all_gizmo_to_group():
    """Convert all gizmo node to group node."""

    for n in nuke.allNodes():
        # Avoid scripted gizmo.
        if nuke.knobChangeds.get(n.Class()):
            continue

        gizmo_to_group(n)
