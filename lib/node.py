# -*- coding=UTF-8 -*-
"""Setup node.  """
from __future__ import absolute_import

import logging
import os
import time

import nuke

import wlf.path

LOGGER = logging.getLogger('com.wlf.node')


def append_knob(node, knob):
    """Add @knob as @node's last knob.  """
    knob_name = knob.name()
    if nuke.exists('{}.{}'.format(node.name(), knob.name())):
        knob.setValue(node[knob_name].value())
        node.removeKnob(node[knob_name])
    node.addKnob(knob)


class ReadNode(object):
    """Modifiled ReadNode by wlf.  """

    tag_knob_name = u'wlf_tag'
    layer_knob_name = u'wlf_layer'

    def __init__(self, node):
        if not isinstance(node, nuke.Node):
            raise TypeError
        n = node
        self._node = n
        self._filename = nuke.filename(n)
        tag = nuke.value(u'{}.{}'.format(n.name(), self.tag_knob_name), '')\
            or self.tag()

        k = nuke.String_Knob(self.tag_knob_name, '标签')
        append_knob(node, k)
        k.setValue(tag)

        layer = wlf.path.get_layer(nuke.filename(n))
        k = nuke.String_Knob(self.layer_knob_name, '层')
        append_knob(node, k)
        k.setValue(layer)

        n.setName('_'.join(i for i in (tag, layer) if i),
                  updateExpressions=True)

    def tag(self):
        """Return Read node tag.  """
        ret = wlf.path.get_tag(self._filename)

        return ret

    def layer(self):
        """Return Read node layer.  """
        return wlf.path.get_layer(self._filename)


def wlf_write_node():
    """Return founded wlf_write node.  """

    n = nuke.toNode('_Write')\
        or nuke.toNode('wlf_Write1')
    if not n:
        nodes = nuke.allNodes('wlf_Write')
        n = nodes and nodes[0]

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


class Last(object):
    """For recording last script infomation"""
    mov_path = None
    jpg_path = None
    mtime = time.localtime()
    name = None
    showed_warning = []

    @classmethod
    def on_load_callback(cls):
        """On close callback.  """
        del cls.showed_warning[:]
        try:
            cls.mtime = time.localtime(
                os.path.getmtime(nuke.scriptName()))
        except RuntimeError:
            pass
        cls.record()

    @classmethod
    def on_save_callback(cls):
        """On close callback.  """
        cls.mtime = time.localtime()
        cls.record()

    @classmethod
    def record(cls):
        """Record information.  """

        try:
            cls.name = nuke.scriptName()
        except RuntimeError:
            pass

        n = wlf_write_node()
        if n:
            cls.jpg_path = nuke.filename(n.node('Write_JPG_1'))
            cls.mov_path = nuke.filename(n.node('Write_MOV_1'))
        else:
            cls.jpg_path = None
            cls.mov_path = None
