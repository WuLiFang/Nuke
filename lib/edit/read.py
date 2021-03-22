# -*- coding=UTF-8 -*-
"""Modify `Read` node.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import re

import cast_unknown as cast
import nuke
from pathlib2_unicode import PurePath

from node import LOGGER, wlf_write_node
from nuketools import undoable_func

from . import core

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text,  Iterable, List


def replace_sequence():
    # TODO: Need refactor and test.
    '''Replace all read node to specified frame range sequence.  '''

    # Prepare Panel
    panel = nuke.Panel(cast.binary('单帧替换为序列'))
    label_path_prefix = cast.binary('限定只替换此文件夹中的读取节点')
    label_first = cast.binary('设置工程起始帧')
    label_last = cast.binary('设置工程结束帧')

    _ = panel.addFilenameSearch(label_path_prefix, b'z:/')
    _ = panel.addExpressionInput(label_first, (
        nuke.Root()[b'first_frame'].value()))
    _ = panel.addExpressionInput(label_last, (
        nuke.Root()[b'last_frame'].value()))

    confirm = panel.show()
    if confirm:
        render_path = os.path.normcase(
            cast.text(panel.value(label_path_prefix)))

        first = int(cast.not_none(panel.value(label_first)))
        last = int(cast.not_none(panel.value(label_last)))
        flag_frame = None

        _ = nuke.Root()[b'proxy'].setValue(False)
        _ = nuke.Root()[b'first_frame'].setValue(first)
        _ = nuke.Root()[b'last_frame'].setValue(last)

        for n in nuke.allNodes(b'Read'):
            file_path = cast.text(nuke.filename(n))
            if os.path.normcase(file_path).startswith(render_path):
                search_result = re.search(r'\.([\d]+)\.', file_path)
                if search_result:
                    flag_frame = search_result.group(1)
                file_path = re.sub(
                    r'\.([\d#]+)\.',
                    lambda matchobj: r'.%0{}d.'.format(len(matchobj.group(1))),
                    file_path)
                _ = n[b'file'].setValue(file_path.encode('utf-8'))
                _ = n[b'format'].setValue(b'HD_1080')
                _ = n[b'first'].setValue(first)
                _ = n[b'origfirst'].setValue(first)
                _ = n[b'last'].setValue(last)
                _ = n[b'origlast'].setValue(last)

        n = wlf_write_node()
        if n:
            if flag_frame:
                flag_frame = int(flag_frame)
                _ = n[b'custom_frame'].setValue(flag_frame)
                nuke.root().setFrame(flag_frame)
            _ = n[b'use_custom_frame'].setValue(True)


def use_relative_path(nodes):
    """Convert given nodes's file knob to relative path."""

    if isinstance(nodes, nuke.Node):
        nodes = [nodes]

    proj_dir = PurePath(nuke.value(b'root.project_directory').decode("utf-8"))
    for n in nodes:
        try:
            path = PurePath(n[b'file'].value().decode("utf-8"))
            _ = n[b'file'].setValue(cast.binary(
                path.relative_to(proj_dir).as_posix()))
        except NameError:
            continue


def reload_all_read_node():
    """Reload all read node by reload button.  """

    for n in nuke.allNodes(b'Read'):
        k = n[b'reload']
        assert isinstance(k, nuke.Script_Knob)
        k.execute()


def set_framerange(first, last, nodes=None):
    # type: (int, int, Iterable[nuke.Node]) -> None
    """Set read nodes framerange.  """

    if nodes is None:
        nodes = nuke.selectedNodes()
    first, last = int(first), int(last)
    for n in nodes:
        if n.Class() == 'Read':
            _ = n[b'first'].setValue(first)
            _ = n[b'origfirst'].setValue(first)
            _ = n[b'last'].setValue(last)
            _ = n[b'origlast'].setValue(last)


def dialog_set_framerange():
    """Dialog for set_framerange.  """

    panel = nuke.Panel(cast.binary('设置帧范围'))
    _ = panel.addExpressionInput(b'first', nuke.value(b'root.first_frame'))
    _ = panel.addExpressionInput(b'last', nuke.value(b'root.last_frame'))
    confirm = panel.show()

    if confirm:
        set_framerange(
            int(cast.not_none(panel.value(b'first'))),
            int(cast.not_none(panel.value(b'last'))),
        )


@undoable_func('合并重复读取节点')
def remove_duplicated_read(
    is_show_result=True,  # type: bool
):  # type: (...) -> None
    """Remove duplicated read to save memory.  """

    nodes = nuke.allNodes(b'Read')
    nodes.sort(key=lambda n: n.ypos())
    distinct_read = []  # type: List[nuke.Node]
    removed_nodes = []  # type: List[Text]

    for n in nodes:
        same_node = _find_same(n, distinct_read)
        if same_node:
            dot = nuke.nodes.Dot(
                inputs=[same_node],
                label='代替: {}\n{}'.format(
                    cast.text(n.name()),
                    cast.text(nuke.filename(n)),
                ).encode('utf-8'),
                hide_input=True)
            dot.setXYpos(n.xpos() + 34, n.ypos() + 57)
            core.replace_node(n, dot)
            n_name = cast.text(n.name())
            removed_nodes.append(n_name)
            LOGGER.info('用 {0} 代替 {1} , 删除 {1}。'.format(
                cast.text(same_node.name()), n_name))
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
