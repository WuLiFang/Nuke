# -*- coding=UTF-8 -*-
"""Node editing core opearations.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import math

import nuke

LOGGER = logging.getLogger(__name__)


def clear_selection():
    """Clear node selection.  """

    for n in nuke.allNodes():
        try:
            selected = n['selected'].value()
        except NameError:
            continue
        if selected:
            n['selected'].setValue(False)


def replace_node(node, repl_node):
    """Replace a node with another in node graph.

    Args:
        node (nuke.Node): Node to be replaced.
        repl_node (nuke.Node): Node to replace.
    """

    nodes = node.dependent(nuke.INPUTS | nuke.HIDDEN_INPUTS, False)
    for n in nodes:
        for i in range(n.inputs()):
            if n.input(i) is node:
                n.setInput(i, repl_node)


def insert_node(node, input_node):
    """Insert @node after @input_node in node graph

    Args:
        node (nuke.Node): Node to insert.
        input_node (nuke.Node): Node as input.
    """

    for n in nuke.allNodes():
        for i in xrange(n.inputs()):
            if n.input(i) is input_node:
                n.setInput(i, node)

    node.setInput(0, input_node)


def set_knobs(node, **knob_values):
    """Set multiple knobs at once.

    Args:
        node (nuke.Node): Node to set knobs.
        **knob_values (any): Use pair of (knob name, value).
    """

    for knob_name, value in knob_values.items():
        try:
            node[knob_name].setValue(value)
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
