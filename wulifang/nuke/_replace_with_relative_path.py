# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import os
import webbrowser

import nuke

from wulifang._util import (
    cast_str,
    cast_text,
    iteritems,
    create_html_url,
)


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Iterable, Iterator


class ResultItem:
    def __init__(self, _knob_fqn, _old_value, _new_value):
        # type: (Text, Text, Text) -> None
        self.knob_fqn = _knob_fqn
        self.old_value = _old_value
        self.new_value = _new_value


def _html(result):
    # type: (Iterable[ResultItem]) -> ...

    yield """\
<style>
    td {
        padding: 8px;
    }
</style>"""
    yield "<h1>替换结果</h1>"
    yield """\
<table>
<tr>
    <th>名称</th>
    <th>原始值</th>
    <th>替换值</th>
</tr>
"""
    for i in result:
        yield """\
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
""" % (
            i.knob_fqn,
            i.old_value,
            i.new_value,
        )
    yield "</table>"


def show(result):
    # type: (Iterable[ResultItem]) -> None

    result = list(result)
    if not result:
        nuke.message(cast_str("没有发现需要替换的文件"))
        return

    webbrowser.open(create_html_url("\n".join(_html(result))))


def _replace_knob(proj_dir, k):
    # type: (Text, nuke.File_Knob) -> Iterator[ResultItem]
    fqn = cast_text(k.fullyQualifiedName())
    old_value = cast_text(k.value())
    if not old_value or not os.path.isabs(old_value):
        return
    try:
        new_value = os.path.relpath(old_value, proj_dir)
        if new_value == old_value:
            return
        k.fromUserText(cast_str(new_value))
    except Exception as ex:
        yield ResultItem(
            fqn,
            old_value,
            "ERROR: %s" % (ex,),
        )
        return
    yield ResultItem(
        fqn,
        old_value,
        new_value,
    )


def replace(nodes):
    # type: (Iterable[nuke.Node]) -> Iterator[ResultItem]
    """Convert given nodes's file knob to relative path."""

    if isinstance(nodes, nuke.Node):
        nodes = [nodes]

    proj_dir = cast_text(nuke.value(cast_str("root.project_directory")))
    if not proj_dir:
        nuke.message(cast_str("未设置工程目录"))
        return
    for n in nodes:
        for _, k in iteritems(n.knobs()):
            if isinstance(k, nuke.File_Knob):
                for i in _replace_knob(proj_dir, k):
                    yield i
