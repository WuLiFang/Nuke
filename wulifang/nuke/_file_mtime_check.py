# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import time
import webbrowser

import nuke

import wulifang
import wulifang.nuke
from wulifang._util import (
    cast_str,
    cast_text,
    escape_html,
    format_time,
    create_html_url,
)
from wulifang.nuke._util import iter_deep_all_nodes, Progress

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterable, Iterator, Text


class Item:
    def __init__(self, node, filename, mtime):
        # type: (nuke.Node, Text, float) -> None
        self.node = node
        self.filename = filename
        self.mtime = mtime


def find(nodes, script_mtime):
    # type: (Iterable[nuke.Node], float) -> Iterator[Item]
    with Progress("检查素材更新") as p:
        for n in nodes:
            if cast_text(n.Class()) not in ("Read", "DeepRead"):
                continue
            p.set_message(cast_text(n.fullName()))
            p.increase()
            mtime_text = n.metadata(cast_str("input/mtime"))
            if mtime_text is None:
                continue
            mtime = time.mktime(
                time.strptime(
                    cast_text(mtime_text),
                    "%Y-%m-%d %H:%M:%S",
                )
            )
            if mtime > script_mtime:
                yield Item(n, cast_text(nuke.filename(n)), mtime)


def _html(script_name, script_mtime, items):
    # type: (Text, float, Iterable[Item]) -> Iterator[Text]

    yield """\
<style>
    td {
        padding: 8px;
    }
</style>"""
    yield "<b>%s</b>" % (escape_html(script_name),)
    yield "<div>上次修改: %s </div>" % (escape_html(format_time(script_mtime)),)
    yield """\
<div>以下素材更新了：
    <table>
        <tr>
            <th>节点</th>
            <th>修改日期</th>
            <th>素材</th>
        </tr>"""
    for i in items:
        yield """\
        <tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
        </tr>""" % (
            escape_html(cast_text(i.node.name())),
            escape_html(format_time(i.mtime)),
            escape_html(i.filename),
        )
    yield """\
    </table>
</div>"""


def show(nodes, verbose=False):
    # type: (Iterable[nuke.Node],bool) -> None
    """Show footage that mtime newer than script mtime."""

    try:
        script_name = cast_text(nuke.scriptName())
    except RuntimeError:
        if verbose:
            nuke.message(cast_str("文件未保存"))
        return
    script_mtime = os.path.getmtime(script_name)

    items = list(find(nodes, script_mtime))
    if not items:
        if verbose:
            nuke.message(cast_str("没有发现更新的素材"))
        return
    html = "\n".join(_html(script_name, script_mtime, items))
    webbrowser.open_new(create_html_url(html))


def _on_script_load():
    show(iter_deep_all_nodes())


def init_gui():
    wulifang.nuke.callback.on_script_load(_on_script_load)
