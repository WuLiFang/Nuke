# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import colorsys
import random

import nuke

import wulifang.nuke
from wulifang._util import cast_str, cast_text


def _on_did_node_create():
    # type: () -> None
    n = nuke.thisNode()
    k = n.knob(cast_str("gl_color"))
    if (
        not isinstance(k, nuke.Color_Knob)
        or k.value()
        or cast_text(n.name()).startswith("_")
    ):
        return
    color = colorsys.hsv_to_rgb(random.random(), 0.8, 1)
    color = tuple(int(i * 255) for i in color)
    k.setValue(color[0] << 24 | color[1] << 16 | color[2] << 8)


def init_gui():
    wulifang.nuke.callback.on_create(_on_did_node_create)
