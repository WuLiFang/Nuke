# -*- coding=UTF-8 -*-
"""Setup node.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

import nuke

from pathlib2_unicode import PurePath
import cast_unknown as cast
import filetools

LOGGER = logging.getLogger('com.wlf.node')


def append_knob(node, knob):
    """Add @knob as @node's last knob.  """

    assert isinstance(node, nuke.Node)
    assert isinstance(knob, nuke.Knob)
    knob_name = knob.name()
    node_name = node.name()
    if nuke.exists(b'%s.%s' % (node_name, knob_name)):
        knob.setValue(node[knob_name].value())
        node.removeKnob(node[knob_name])
    node.addKnob(knob)


class ReadNode(object):
    """Read node with tag and layer information  """

    tag_knob_name = 'wlf_tag'
    layer_knob_name = 'wlf_layer'

    def __init__(self, node):
        assert isinstance(node, nuke.Node)
        n = node

        self._filename = cast.binary(nuke.filename(n))
        path = PurePath(cast.text(self._filename))

        tag = cast.text(nuke.value(
            '{}.{}'.format(cast.text(n.name()),
                           self.tag_knob_name).encode('utf-8'),
            b'') or filetools.get_tag(cast.text(path)))

        k = nuke.String_Knob(
            cast.binary(self.tag_knob_name),
            cast.binary('标签'),
        )
        append_knob(node, k)
        k.setValue(tag)

        layer = filetools.get_layer(cast.text(path))
        k = nuke.String_Knob(cast.binary(
            self.layer_knob_name), '层'.encode('utf-8'))
        append_knob(node, k)
        k.setValue(layer)

        n.setName('_'.join(i for i in (tag, layer) if i).encode('utf-8'),
                  updateExpressions=True)


def wlf_write_node():
    """Return founded wlf_write node.  """

    n = (nuke.toNode(b'_Write')
         or nuke.toNode(b'wlf_Write1'))
    if not n:
        nodes = nuke.allNodes(b'wlf_Write')
        if nodes:
            n = nodes[0]
    if not n:
        raise ValueError('Not found wlf_Write Node.')
    return n


def parent_backdrop(node):
    """ Return direct parent backdrop for @node.  """

    backdrops = nuke.allNodes(b'BackdropNode')
    nodes = set()
    list(nodes.union(n.getNodes()) for n in backdrops)
    backdrops = set(backdrops) - nodes
    for n in backdrops:
        if node in n.getNodes():
            return n
