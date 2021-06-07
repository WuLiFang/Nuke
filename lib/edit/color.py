# -*- coding=UTF-8 -*-
"""Modify node color.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import colorsys
import random


def set_random_glcolor(n):
    """Set glcolor of node to a hue random color.

    Args:
        n (nuke.Node): Node to manipulate.
    """

    if (
        "gl_color" in n.knobs()
        and not n["gl_color"].value()
        and not n.name().startswith("_")
    ):

        color = colorsys.hsv_to_rgb(random.random(), 0.8, 1)
        color = tuple(int(i * 255) for i in color)
        n["gl_color"].setValue(color[0] << 24 | color[1] << 16 | color[2] << 8)
