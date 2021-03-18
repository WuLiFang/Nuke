# -*- coding=UTF-8 -*-
"""Cleanup comp script.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke
import cast_unknown as cast
from . import core


import logging
LOGGER = logging.getLogger(__name__)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterable


def delete_unused_nodes(
    nodes=None,  # type: Iterable[nuke.Node]
    message=False,  # type: bool
):
    """Delete all unused nodes."""

    if nodes is None:
        nodes = nuke.allNodes()
    nodes = sorted(nodes, key=lambda n: (n.ypos(), n.xpos()), reverse=True)

    # Split disabled nodes.
    disabled_nodes = [n for n in nodes if _is_disabled_and_no_expression(n)]

    for n in disabled_nodes:
        node_name = cast.text(n.name())
        core.replace_node(n, n.input(0))
        LOGGER.info('分离已禁用的节点: {}'.format(node_name))

    # Delete unused nodes.
    is_used_result_cache = {}
    unused_nodes = [n for n in nodes if not _is_used(n, is_used_result_cache)]
    for n in unused_nodes:
        node_name = cast.text(n.name())
        nuke.delete(n)
        LOGGER.info('删除节点: {}'.format(node_name))
    LOGGER.info('删除了 {} 个无用节点.'.format(len(unused_nodes)))

    if message:
        nuke.message(
            '<font size=5>删除了 {} 个未使用的节点。</font>\n'
            '<i>名称以"_"(下划线)开头的节点及其上游节点将不会被删除</i>'.format(
                len(unused_nodes)).encode('utf-8'))


def _is_disabled_and_no_expression(n):
    try:
        disable_knob = n['disable']
        if (disable_knob.value()
                and not disable_knob.hasExpression()
                and not n.dependent(nuke.EXPRESSIONS)):
            return True
    except NameError:
        pass
    return False


def _is_used(n, cache):
    assert isinstance(n, nuke.Node)
    assert isinstance(cache, dict)
    node_name = cast.text(n.name())
    if n in cache:
        return cache[n]

    if (node_name.startswith('_')
            or node_name == 'VIEWER_INPUT'
            or cast.text(n.Class()) in ('BackdropNode',
                                        'Read',
                                        'Write',
                                        'Viewer',
                                        'GenerateLUT',
                                        'wlf_Write')):
        ret = True
    else:
        ret = (not _is_disabled_and_no_expression(n)
               and any(_is_used(n, cache) for n in n.dependent()))

    cache[n] = ret
    return ret
