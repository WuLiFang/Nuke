# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

def wlf_write_node():
    # type: () -> nuke.Group
    """Return founded wlf_write node."""

    n = nuke.toNode(b"_Write") or nuke.toNode(b"wlf_Write1")
    if not n:
        nodes = nuke.allNodes(b"wlf_Write")
        if nodes:
            n = nodes[0]
    if not n:
        raise ValueError("Not found wlf_Write Node.")
    assert isinstance(n, nuke.Group), "wlf_Write should be a group"
    return n
