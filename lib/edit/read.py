# -*- coding=UTF-8 -*-
"""Modify `Read` node.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import re

import nuke

from node import wlf_write_node
from nuketools import undoable_func, utf8
from wlf.codectools import get_unicode as u
from wlf.codectools import u_print
from pathlib2_unicode import PurePath

from . import core


def replace_sequence():
    # TODO: Need refactor and test.
    '''Replace all read node to specified frame range sequence.  '''

    # Prepare Panel
    panel = nuke.Panel(b'单帧替换为序列')
    label_path_prefix = b'限定只替换此文件夹中的读取节点'
    label_first = b'设置工程起始帧'
    label_last = b'设置工程结束帧'

    panel.addFilenameSearch(label_path_prefix, 'z:/')
    panel.addExpressionInput(label_first, int(
        nuke.Root()['first_frame'].value()))
    panel.addExpressionInput(label_last, int(
        nuke.Root()['last_frame'].value()))

    confirm = panel.show()
    if confirm:
        render_path = os.path.normcase(u(panel.value(label_path_prefix)))

        first = int(panel.value(label_first))
        last = int(panel.value(label_last))
        flag_frame = None

        nuke.Root()[b'proxy'].setValue(False)
        nuke.Root()[b'first_frame'].setValue(first)
        nuke.Root()[b'last_frame'].setValue(last)

        for n in nuke.allNodes('Read'):
            file_path = u(nuke.filename(n))
            if os.path.normcase(file_path).startswith(render_path):
                search_result = re.search(r'\.([\d]+)\.', file_path)
                if search_result:
                    flag_frame = search_result.group(1)
                file_path = re.sub(
                    r'\.([\d#]+)\.',
                    lambda matchobj: r'.%0{}d.'.format(len(matchobj.group(1))),
                    file_path)
                n[b'file'].setValue(file_path.encode('utf-8'))
                n[b'format'].setValue(b'HD_1080')
                n[b'first'].setValue(first)
                n[b'origfirst'].setValue(first)
                n[b'last'].setValue(last)
                n[b'origlast'].setValue(last)

        n = wlf_write_node()
        if n:
            if flag_frame:
                flag_frame = int(flag_frame)
                n[b'custom_frame'].setValue(flag_frame)
                nuke.frame(flag_frame)
            n[b'use_custom_frame'].setValue(True)


def use_relative_path(nodes):
    """Convert given nodes's file knob to relative path."""

    if isinstance(nodes, nuke.Node):
        nodes = [nodes]

    proj_dir = PurePath(nuke.value('root.project_directory').decode("utf-8"))
    for n in nodes:
        try:
            path = PurePath(n['file'].value().decode("utf-8"))
            n['file'].setValue(utf8(path.relative_to(proj_dir).as_posix()))
        except NameError:
            continue


def reload_all_read_node():
    """Reload all read node by reload button.  """

    for n in nuke.allNodes('Read'):
        n['reload'].execute()


def set_framerange(first, last, nodes=None):
    """Set read nodes framerange.  """

    if nodes is None:
        nodes = nuke.selectedNodes()
    first, last = int(first), int(last)
    for n in nodes:
        if n.Class() == 'Read':
            n['first'].setValue(first)
            n['origfirst'].setValue(first)
            n['last'].setValue(last)
            n['origlast'].setValue(last)


def dialog_set_framerange():
    """Dialog for set_framerange.  """

    panel = nuke.Panel('设置帧范围')
    panel.addExpressionInput('first', nuke.numvalue('root.first_frame'))
    panel.addExpressionInput('last', nuke.numvalue('root.last_frame'))
    confirm = panel.show()

    if confirm:
        set_framerange(panel.value('first'), panel.value('last'))


@undoable_func('合并重复读取节点')
def remove_duplicated_read(is_show_result=True):
    """Remove duplicated read to save memory.  """

    nodes = nuke.allNodes('Read')
    nodes.sort(key=lambda n: n.ypos())
    distinct_read = []
    removed_nodes = []

    for n in nodes:
        same_node = _find_same(n, distinct_read)
        if same_node:
            dot = nuke.nodes.Dot(
                inputs=[same_node],
                label='代替: {}\n{}'.format(u(n.name()), u(
                    nuke.filename(n))).encode('utf-8'),
                hide_input=True)
            dot.setXYpos(n.xpos() + 34, n.ypos() + 57)
            core.replace_node(n, dot)
            n_name = u(n.name())
            removed_nodes.append(n_name)
            u_print('用 {0} 代替 {1} , 删除 {1}。'.format(
                u(same_node.name()), n_name))
            nuke.delete(n)
        else:
            distinct_read.append(n)

    if not is_show_result:
        return
    if removed_nodes:
        nuke.message('合并时删除了{}个节点: \n{}'.format(
            len(removed_nodes), ', '.join(removed_nodes)).encode('utf-8'))
    else:
        nuke.message('没有发现重复读取节点。'.encode('utf-8'))


def _find_same(node, nodes):
    keys = ('file', 'proxy', 'first', 'last',
            'frame_mode', 'frame', 'disable')
    try:
        return next(n for n in nodes
                    if all(n[j].value() == node[j].value() for j in keys))
    except StopIteration:
        return None
