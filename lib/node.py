# -*- coding=UTF-8 -*-
"""Setup node.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

import nuke

from wlf.codectools import get_unicode as u
from wlf.path import PurePath

LOGGER = logging.getLogger('com.wlf.node')


def append_knob(node, knob):
    """Add @knob as @node's last knob.  """

    knob_name = u(knob.name())
    node_name = u(node.name())
    if nuke.exists('{}.{}'.format(node_name, knob_name).encode('utf-8')):
        knob.setValue(node[knob_name.encode('utf-8')].value())
        node.removeKnob(node[knob_name.encode('utf-8')])
    node.addKnob(knob)


class ReadNode(object):
    """Read node with tag and layer information  """

    tag_knob_name = 'wlf_tag'
    layer_knob_name = 'wlf_layer'

    def __init__(self, node):
        assert isinstance(node, nuke.Node)
        n = node

        self._filename = u(nuke.filename(n))
        path = PurePath(self._filename)

        tag = (nuke.value(
            '{}.{}'.format(u(n.name()),
                           self.tag_knob_name).encode('utf-8'),
            '') or path.tag)

        k = nuke.String_Knob(self.tag_knob_name, '标签'.encode('utf-8'))
        append_knob(node, k)
        k.setValue(tag)

        layer = path.layer
        k = nuke.String_Knob(self.layer_knob_name, '层'.encode('utf-8'))
        append_knob(node, k)
        k.setValue(path.layer)

        n.setName('_'.join(i for i in (tag, layer) if i).encode('utf-8'),
                  updateExpressions=True)


def wlf_write_node():
    """Return founded wlf_write node.  """

    n = (nuke.toNode('_Write')
         or nuke.toNode('wlf_Write1'))
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
