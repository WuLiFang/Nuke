# -*- coding=UTF-8 -*-
"""Cleanup comp script.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

from wlf.codectools import get_unicode as u
from wlf.codectools import u_print
from wlf.progress import DefaultHandler, progress

from . import core


def delete_unused_nodes(nodes=None, message=False):
    """Delete all unused nodes."""

    if nodes is None:
        nodes = nuke.allNodes()
    handler = DefaultHandler()
    handler.message_factory = lambda n: n.name()
    unused_nodes = [n for n in progress(nodes, '清除无用节点', handler)
                    if not _is_used(n)]
    for n in unused_nodes:
        node_name = u(n.name())
        core.replace_node(n, n.input(0))
        nuke.delete(n)
        u_print('删除节点: {}'.format(node_name))
    u_print('删除了 {} 个无用节点.'.format(len(unused_nodes)))

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


def _is_used(n):
    node_name = u(n.name())
    if (node_name.startswith('_')
            or node_name == 'VIEWER_INPUT'
            or n.Class() in ('BackdropNode',
                             'Read',
                             'Write',
                             'Viewer',
                             'GenerateLUT',
                             'wlf_Write')):
        return True

    return (not _is_disabled_and_no_expression(n)
            and any(_is_used(n) for n in n.dependent()))
