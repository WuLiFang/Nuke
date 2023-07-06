# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke


from wulifang._util import cast_str


def selected_node():
    """nuke.selectedNode with a error message.

    Raises:
        ValueError: when no node selected

    Returns:
        nuke.Node: selected node.
    """
    try:
        return nuke.selectedNode()
    except ValueError as ex:
        nuke.message(cast_str("请选择节点"))
        raise ex
