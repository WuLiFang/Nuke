# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

def is_node_deleted(node):
    # type: (nuke.Node) -> bool
    """Check if node already deleted."""

    try:
        _ = repr(node)
        return False
    except ValueError:
        return True
