# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke
from wulifang._util import cast_str


def wlf_write_node():
    # type: () -> nuke.Group
    """Return founded wlf_write node."""

    n = nuke.toNode(cast_str("_Write")) or nuke.toNode(cast_str("wlf_Write1"))
    if not n:
        nodes = nuke.allNodes(cast_str("wlf_Write"))
        if nodes:
            n = nodes[0]
    if not n:
        raise ValueError("`wlf_Write` node not found")
    assert isinstance(n, nuke.Group), "`wlf_Write` should be a group"
    return n
