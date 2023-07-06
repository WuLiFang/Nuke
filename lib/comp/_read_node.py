# -*- coding=UTF-8 -*-
"""Setup node.  """

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke

from wulifang.vendor.pathlib2_unicode import PurePath
import wulifang.vendor.cast_unknown as cast
from wulifang._util import tag_from_filename, layer_from_filename


def _append_knob(node, knob):
    """Add @knob as @node's last knob."""

    assert isinstance(node, nuke.Node)
    assert isinstance(knob, nuke.Knob)
    knob_name = knob.name()
    node_name = node.name()
    if nuke.exists(b"%s.%s" % (node_name, knob_name)):
        _ = knob.setValue(node[knob_name].value())
        node.removeKnob(node[knob_name])
    node.addKnob(knob)


class ReadNode(object):
    """Read node with tag and layer information"""

    tag_knob_name = "wlf_tag"
    layer_knob_name = "wlf_layer"

    def __init__(self, node):
        assert isinstance(node, nuke.Node)
        n = node

        self._filename = cast.binary(nuke.filename(n))
        path = PurePath(cast.text(self._filename))

        tag = cast.text(
            nuke.value(
                "{}.{}".format(cast.text(n.name()), self.tag_knob_name).encode("utf-8"),
                b"",
            )
            or tag_from_filename(cast.text(path))
        )

        k = nuke.String_Knob(
            cast.binary(self.tag_knob_name),
            cast.binary("标签"),
        )
        _append_knob(node, k)
        k.setValue(tag)

        layer = layer_from_filename(cast.text(path))
        k = nuke.String_Knob(cast.binary(self.layer_knob_name), "层".encode("utf-8"))
        _append_knob(node, k)
        k.setValue(layer)

        n.setName(
            "_".join(i for i in (tag, layer) if i).encode("utf-8"),
            updateExpressions=True,
        )
