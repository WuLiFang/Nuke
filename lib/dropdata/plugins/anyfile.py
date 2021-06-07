# -*- coding=UTF-8 -*-
"""Handle any file nuke can read.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke
import cast_unknown as cast

from ..core import HOOKIMPL

# pylint: disable=missing-docstring


@HOOKIMPL(trylast=True)
def create_node(filename, context):
    if context["is_created"]:
        return None
    n = nuke.nodes.Read()
    cast.instance(n[b"file"], nuke.File_Knob).fromUserText(
        filename.encode("utf-8"),
    )
    if n.hasError():
        nuke.delete(n)
        return None
    return [n]
