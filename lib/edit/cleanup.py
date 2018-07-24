# -*- coding=UTF-8 -*-
"""Cleanup comp script.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

from wlf.progress import DefaultHandler, progress


def delete_unused_nodes(nodes=None, message=False):
    # TODO: Need refactor and test.
    """Delete all unused nodes."""

    def _is_used(n):
        if n.name().startswith('_')\
                or n.Class() in \
                ['BackdropNode', 'Read', 'Write', 'Viewer',
                 'GenerateLUT', 'wlf_Write']\
                or n.name() == 'VIEWER_INPUT':
            return True
        nodes_dependent_this = (n for n in n.dependent()
                                if n.Class() not in ['']
                                or n.name().startswith('_'))
        return any(nodes_dependent_this)

    if nodes is None:
        nodes = nuke.allNodes()
    count = 0
    handler = DefaultHandler()
    handler.message_factory = lambda n: n.name()
    while True:
        for n in progress(nodes, '清除无用节点', handler):
            if not _is_used(n):
                nuke.delete(n)
                nodes.remove(n)
                count += 1
                break
        else:
            break

    print('Deleted {} unused nodes.'.format(count))
    if message:
        nuke.message(
            b'<font size=5>删除了 {} 个未使用的节点。</font>\n'
            b'<i>名称以"_"(下划线)开头的节点及其上游节点将不会被删除</i>'.format(count))
