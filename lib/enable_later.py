# -*- coding=UTF-8 -*-
# pyright: strict
"""For disable nodes then enable them on script save.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

import callback
from nodeutil import Nodes

ENABLE_MARK = b'_enable_'

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Union, Iterable, Set


def mark_enable(nodes):
    # type: (Union[Iterable[nuke.Node], nuke.Node]) -> None
    """Mark nodes enable later then disabled them.  """

    if isinstance(nodes, nuke.Node):
        nodes = (nodes,)
    for n in nodes:
        try:
            label_knob = n[b'label']
            label = label_knob.value()
            if ENABLE_MARK not in label:
                _ = label_knob.setValue(label + b"\n" + ENABLE_MARK)
            _ = n[b'disable'].setValue(True)
        except NameError:
            continue


def marked_nodes():
    """ Get marked nodes.

    Returns:
        Nodes: marked nodes.
    """

    ret = set()  # type: Set[nuke.Node]
    for n in nuke.allNodes():
        try:
            label = n[b'label'].value()
            if ENABLE_MARK in label:
                ret.add(n)
        except NameError:
            continue
    return Nodes(ret)


def setup():
    def _enable_node():
        if nuke.numvalue(b'preferences.wlf_enable_node', 0.0):
            marked_nodes().enable()

    callback.CALLBACKS_ON_SCRIPT_SAVE.append(_enable_node)
