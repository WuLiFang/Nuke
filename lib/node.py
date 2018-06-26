# -*- coding=UTF-8 -*-
"""Setup node.  """
from __future__ import absolute_import

import logging
import os
import time

import nuke

from wlf.path import PurePath

LOGGER = logging.getLogger('com.wlf.node')


def append_knob(node, knob):
    """Add @knob as @node's last knob.  """
    knob_name = knob.name()
    if nuke.exists('{}.{}'.format(node.name(), knob.name())):
        knob.setValue(node[knob_name].value())
        node.removeKnob(node[knob_name])
    node.addKnob(knob)


class ReadNode(object):
    """Read node with tag and layer information  """

    tag_knob_name = u'wlf_tag'
    layer_knob_name = u'wlf_layer'

    def __init__(self, node):
        assert isinstance(node, nuke.Node)
        n = node

        self._filename = nuke.filename(n)
        path = PurePath(self._filename)

        tag = (nuke.value(u'{}.{}'.format(n.name(), self.tag_knob_name), '')
               or path.tag)

        k = nuke.String_Knob(self.tag_knob_name, '标签')
        append_knob(node, k)
        k.setValue(tag)

        layer = path.layer
        k = nuke.String_Knob(self.layer_knob_name, '层')
        append_knob(node, k)
        k.setValue(path.layer)

        n.setName('_'.join(i for i in (tag, layer) if i),
                  updateExpressions=True)


def wlf_write_node():
    """Return founded wlf_write node.  """

    n = nuke.toNode('_Write')\
        or nuke.toNode('wlf_Write1')
    if not n:
        nodes = nuke.allNodes('wlf_Write')
        n = nodes and nodes[0]
    if not n:
        raise ValueError('Not found wlf_Write Node.')
    return n


def parent_backdrop(node):
    """ Return direct parent backdrop for @node.  """
    backdrops = nuke.allNodes('BackdropNode')
    nodes = set()
    list(nodes.union(n.getNodes()) for n in backdrops)
    backdrops = set(backdrops) - nodes
    for n in backdrops:
        if node in n.getNodes():
            return n
