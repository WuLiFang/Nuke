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
    count = 0
    handler = DefaultHandler()
    handler.message_factory = lambda n: n.name()
    for n in progress(nodes, '清除无用节点', handler):
        if _split_if_disabled(n) or not _is_used(n):
            nuke.delete(n)
            count += 1
    u_print('删除了 {} 个无用节点.'.format(count))
    if message:
        nuke.message(
            '<font size=5>删除了 {} 个未使用的节点。</font>\n'
            '<i>名称以"_"(下划线)开头的节点及其上游节点将不会被删除</i>'.format(
                count).encode('utf-8'))


def _split_if_disabled(n):
    try:
        disable_knob = n['disable']
        if (disable_knob.value()
                and not disable_knob.hasExpression()
                and not n.dependent(nuke.EXPRESSIONS)):
            core.replace_node(n, n.input(0))
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

    return any(_is_used(n) for n in n.dependent())
