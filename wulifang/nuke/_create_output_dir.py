# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import os

import nuke


from wulifang._util import cast_text, cast_str
import wulifang.nuke


def create(n):
    # type: (nuke.Node) -> None

    k = n.knob(cast_str("disable"))
    if not isinstance(k, nuke.Boolean_Knob) or k.value():
        return

    filename = cast_text(nuke.filename(n))
    if filename:
        target_dir = os.path.dirname(filename)
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)


def _on_will_render():
    create(nuke.thisNode())


def init():
    wulifang.nuke.callback.on_will_render(_on_will_render)
