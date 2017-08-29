# -*- coding=UTF-8 -*-
"""Setup node.  """
import os

import nuke

import wlf.files

__version__ = '0.3.0'


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

        layer = wlf.files.get_layer(nuke.filename(n))
        k = nuke.String_Knob(self.layer_knob_name, '层')
        append_knob(node, k)
        k.setValue(layer)

        n.setName('_'.join(i for i in (tag, layer) if i),
                  updateExpressions=True)

    def tag(self):
        """Return Read node tag.  """
        ret = wlf.files.get_tag(self._filename)

        return ret

    def layer(self):
        """Return Read node layer.  """
        return wlf.files.get_layer(self._filename)


def wlf_write_node():
    """Return founded wlf_write node.  """

    n = nuke.toNode('_Write')\
        or nuke.toNode('wlf_Write1')\
        or (nuke.allNodes('wlf_Write') and nuke.allNodes('wlf_Write')[0])

    return n


def get_upstream_nodes(nodes):
    """ Return all nodes in the tree of the node. """
    ret = set()
    if isinstance(nodes, nuke.Node):
        nodes = [nodes]

    nodes = list(nodes)
    while nodes:
        deps = nuke.dependencies(nodes, nuke.INPUTS | nuke.HIDDEN_INPUTS)
        nodes = [n for n in deps if n not in ret]
        ret.update(set(deps))
    return ret


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

    @classmethod
    def on_load_callback(cls):
        """On close callback.  """
        cls.record()

    @classmethod
    def record(cls):
        """Record information.  """
        try:
            cls.mov_path = os.path.dirname(
                nuke.filename(wlf_write_node().node('Write_MOV_1'))) or cls.mov_path
        except AttributeError:
            print('Can not record last script information')
