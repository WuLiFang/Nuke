# -*- coding=UTF-8 -*-
"""Node editing core operations.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import math

import nuke
import six

import cast_unknown as cast

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any

LOGGER = logging.getLogger(__name__)


def clear_selection():
    """Clear node selection.  """

    for n in nuke.allNodes():
        try:
            selected = n[b'selected'].value()
        except NameError:
            continue
        if selected:
            _ = n[b'selected'].setValue(False)


def replace_node(
    node,  # type: nuke.Node
    repl_node,  # type: nuke.Node
):  # type: (...) -> None
    """Replace a node with another in node graph.

    Args:
        node (nuke.Node): Node to be replaced.
        repl_node (nuke.Node): Node to replace.
    """

    nodes = node.dependent(nuke.INPUTS | nuke.HIDDEN_INPUTS, False)
    for n in nodes:
        for i in range(n.inputs()):
            if n.input(i) is node:
                _ = n.setInput(i, repl_node)


def insert_node(
    node,  # type: nuke.Node
    input_node,  # type: nuke.Node
):  # type: (...) -> None
    """Insert @node after @input_node in node graph

    Args:
        node (nuke.Node): Node to insert.
        input_node (nuke.Node): Node as input.
    """

    for n in nuke.allNodes():
        for i in six.moves.range(n.inputs()):
            if n.input(i) is input_node:
                _ = n.setInput(i, node)

    _ = node.setInput(0, input_node)


def set_knobs(
    node,  # type: nuke.Node
    **knob_values  # type: Any
):
    """Set multiple knobs at once.

    Args:
        node (nuke.Node): Node to set knobs.
        **knob_values (any): Use pair of (knob name, value).
    """

    for knob_name, value in knob_values.items():
        try:
            _ = node[cast.binary(knob_name)].setValue(value)
        except (AttributeError, NameError, TypeError):
            LOGGER.debug('Can not set knob: %s.%s to %s',
                         node.name(), knob_name, value)


def transfer_flags(src, dst):
    """Transfer flag from knob to another.

    Args:
        src (nuke.Knob): Get flags from this knob.
        dst (nuke.Knob): Set flags to this knob.
    """

    assert isinstance(src, nuke.Knob)
    assert isinstance(dst, nuke.Knob)

    # Set all possible flag.
    for flag in [pow(2, n) for n in range(31)]:
        if src.getFlag(flag):
            dst.setFlag(flag)
        else:
            dst.clearFlag(flag)


def all_flags():
    """Get all flags in nuke.

    Returns:
        dict: Flag name as key, flag value as value.
    """

    ret = dict()

    for attr in sorted(dir(nuke), key=lambda x: getattr(nuke, x)):
        value = getattr(nuke, attr)
        if isinstance(value, int) and value > 0:
            _log = math.log(value, 2)
            if int(_log) == _log:
                ret[attr] = value

    return ret
