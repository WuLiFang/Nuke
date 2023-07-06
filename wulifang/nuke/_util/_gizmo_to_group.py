# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke


from wulifang._util import cast_str


def gizmo_to_group(gizmo):
    # type: (nuke.Gizmo) -> nuke.Group
    """Convert given gizmo node to group node."""

    selected = gizmo[cast_str("selected")].value()
    name = gizmo[cast_str("name")].value()
    xpos = gizmo.xpos()
    ypos = gizmo.ypos()

    group = gizmo.makeGroup()
    # Set Input.
    for i in range(gizmo.inputs()):
        group.setInput(i, gizmo.input(i))
    # Set Output.
    for n in nuke.allNodes():
        for i in range(n.inputs()):
            if n.input(i) is gizmo:
                n.setInput(i, group)

    # Set position and name.
    if gizmo.shown():
        group.showControlPanel()

    nuke.delete(gizmo)
    group.setXYpos(xpos, ypos)
    group.setName(name)
    group[cast_str("selected")].setValue(selected)

    return group
