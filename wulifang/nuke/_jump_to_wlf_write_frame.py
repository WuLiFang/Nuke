# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

import wulifang.nuke

from wulifang._util import (
    cast_str,
    cast_int,
)
from wulifang.nuke._util import (
    wlf_write_node,
    knob_of,
)


def _on_script_save():
    if nuke.numvalue(cast_str("preferences.wlf_jump_frame"), 0.0):
        try:
            n = wlf_write_node()
        except ValueError:
            return
        if n:
            nuke.frame(cast_int(knob_of(n, "frame", nuke.Array_Knob).value()))
            nuke.root().setModified(False)


def init_gui():
    wulifang.nuke.callback.on_script_save(_on_script_save)
