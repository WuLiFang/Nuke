# -*- coding=UTF-8 -*-
"""Offset read node to match project settings.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from ..core import HOOKIMPL
import cast_unknown as cast

# pylint: disable=missing-docstring


@HOOKIMPL
def after_created(nodes):
    if not nodes:
        return
    n = nodes[0]
    _ = nuke.zoom(cast.not_none(nuke.zoom()), (n.xpos(), n.ypos()))
