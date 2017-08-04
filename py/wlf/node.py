# -*- coding=UTF-8 -*-
"""Setup node.  """


import nuke

import wlf.files


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
        self._node = node
        print(node.name())
        n = node
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
        filename = nuke.filename(self._node)
        ret = wlf.files.get_tag(filename)

        return ret

    def layer(self):
        """Return Read node layer.  """
        return wlf.files.get_layer(nuke.filename(self._node))
