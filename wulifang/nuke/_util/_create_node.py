# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang._util import (
    cast_str,
)
from ._knob_of import knob_of

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional, Sequence


def create_node(
    class_,  # type: Text
    tcl="",  # type: Text
    inputs=(),  # type: Sequence[Optional[nuke.Node]]
    name="",  # type: Text
    label="",  # type: Text
    tile_color=0x00000000,  # type: int
    gl_color=0x00000000,  # type: int
    selected=False,  # type: Optional[bool]
    xpos=None,  # type: Optional[int]
    ypos=None,  # type: Optional[int]
    hide_input=None,  # type: Optional[bool]
    show_control_panel=False,  # type: bool
):
    # type: (...) -> nuke.Node
    n = nuke.createNode(cast_str(class_), cast_str(tcl), show_control_panel)
    for index, i in enumerate(inputs):
        n.setInput(index, i)
    if name:
        n.setName(cast_str(name))
    if xpos is not None:
        n.setXpos(xpos)
    if ypos is not None:
        n.setYpos(ypos)
    if selected is not None:
        n.setSelected(selected)
    if label:
        knob_of(n, "label", nuke.String_Knob).setValue(cast_str(label))
    if tile_color:
        knob_of(n, "tile_color", nuke.ColorChip_Knob).setValue(tile_color)
    if gl_color:
        knob_of(n, "gl_color", nuke.ColorChip_Knob).setValue(gl_color)
    if hide_input:
        knob_of(n, "hide_input", nuke.Boolean_Knob).setValue(hide_input)
    return n
