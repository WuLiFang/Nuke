# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from ._optional_knob_of import optional_knob_of


def reload_node(node):
    # type: (nuke.Node) -> None

    k = optional_knob_of(node, "reload", nuke.Script_Knob)
    if k:
        k.execute()
