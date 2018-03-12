# -*- coding=UTF-8 -*-
"""For disable nodes then enable them on script save.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

import callback
from nuketools import Nodes


def mark_enable(nodes):
    """Mark nodes enable later then disabled them.  """

    if isinstance(nodes, nuke.Node):
        nodes = (nodes)
    for n in nodes:
        try:
            label_knob = n['label']
            label = u(label_knob.value())
            if ENABLE_MARK not in label:
                label_knob.setValue(
                    '{}\n{}'.format(label, ENABLE_MARK).encode('utf-8'))
            n['disable'].setValue(True)
        except NameError:
            continue


def marked_nodes():
    """ Get marked nodes.

    Returns:
        Nodes: maked nodes.
    """

    ret = set()
    for n in nuke.allNodes():
        try:
            if ENABLE_MARK in u(n['label'].value()):
                ret.add(n)
        except NameError:
            continue
    return Nodes(ret)


def setup():
    def _enable_node():
        if nuke.numvalue('preferences.wlf_enable_node', 0.0):
            marked_nodes().enable()

    callback.CALLBACKS_ON_SCRIPT_SAVE.append(_enable_node)
