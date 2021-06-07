# -*- coding=UTF-8 -*-
"""Nuke script file handle.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from ..core import HOOKIMPL

# pylint: disable=missing-docstring


@HOOKIMPL
def create_node(filename, context):
    if not filename.lower().endswith(".nk"):
        return None
    n = nuke.nodes.Group(label=filename.encode("utf-8"))
    assert isinstance(n, nuke.Group)
    n.setName(b"Group_import_1")
    with n:
        nuke.scriptReadFile(filename.encode("utf-8"))
    k = nuke.PyScript_Knob(
        b"expand", "展开组".encode("utf-8"), b"nuke.thisNode().expand()"
    )
    n.addKnob(k)
    context["is_created"] = True
    return [n]
