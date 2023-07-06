# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false
"""For disable nodes then enable them on script save.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke


from wulifang._util import cast_str, cast_iterable, cast_text, assert_isinstance
from wulifang.nuke._util import NodeList

_ENABLE_MARK = "_enable_"

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Union, Iterable, Set

from wulifang._util import cast_str
import wulifang.nuke


def mark(nodes):
    # type: (Union[Iterable[nuke.Node], nuke.Node]) -> None
    """Mark nodes enable later then disabled them."""

    for n in cast_iterable(nodes):
        try:
            label_knob = assert_isinstance(n[cast_str("label")], nuke.String_Knob)
            label = cast_text(label_knob.value())
            if _ENABLE_MARK not in label:
                label_knob.setValue(cast_str(label + "\n" + _ENABLE_MARK))
            assert_isinstance(
                n[cast_str("disable")],
                nuke.Boolean_Knob,
            ).setValue(True)
        except NameError:
            continue


def nodes():
    """Get marked nodes.

    Returns:
        Nodes: marked nodes.
    """

    ret = set()  # type: Set[nuke.Node]
    for n in nuke.allNodes():
        try:
            label = cast_text(n[cast_str("label")].value())
            if _ENABLE_MARK in label:
                ret.add(n)
        except NameError:
            continue
    return ret


def init_gui():
    def _enable_node():
        if nuke.numvalue(cast_str("preferences.wlf_enable_node"), 0.0):
            NodeList(nodes()).enable()

    wulifang.nuke.callback.on_script_save(_enable_node)
