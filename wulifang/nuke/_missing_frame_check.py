# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import webbrowser

import nuke

import wulifang
import wulifang.nuke
from wulifang._util import cast_str, cast_text, escape_html, create_html_url
from wulifang.nuke._util import (
    iter_deep_all_nodes,
    Progress,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterable, Text, Iterator


class Item:
    def __init__(self, node, filename, frame_ranges):
        # type: (nuke.Node, Text, nuke.FrameRanges) -> None
        self.node = node
        self.filename = filename
        self.frame_ranges = frame_ranges


def _html(items):
    # type: (list[Item]) -> Iterator[Text]

    yield """\
<style>
    td {
        padding: 8px;
    }
</style>"""
    yield """\
<table>
    <tr>
        <th>节点</th>
        <th>缺帧</th>
        <th>素材</th>
    </tr>"""

    for i in items:
        yield """\
    <tr>
        <td>%s</td>
        <td>
            <span style="color:red">%s</span>
        </td>
        <td>%s</td>
    </tr>""" % (
            escape_html(cast_text(i.node.name())),
            escape_html(cast_text(i.frame_ranges)),
            escape_html(i.filename),
        )

    yield "</table>"


def find(nodes):
    # type: (Iterable[nuke.Node]) -> Iterator[Item]
    with Progress("检查缺帧") as p:
        for n in nodes:
            if cast_text(n.Class()) not in ("Read", "DeepRead"):
                continue
            p.set_message(cast_text(n.fullName()))
            p.increase()
            filename = cast_text(nuke.filename(n))
            frame_ranges = list(
                wulifang.file.missing_frames(filename, n.firstFrame(), n.lastFrame())
            )
            if frame_ranges:
                yield (
                    Item(
                        n,
                        filename,
                        nuke.FrameRanges(frame_ranges),
                    )
                )


def show(items, verbose=False):
    # type: (Iterable[Item], bool) -> None
    items = list(items)
    html = "\n".join(_html(items))

    if not items:
        if verbose:
            nuke.message(cast_str("没有发现缺帧素材"))
        return

    if not nuke.GUI:
        wulifang.message.info(
            "missing frame: %s"
            % (
                "%s: %s %s"
                % (
                    cast_text(i.node.name()),
                    cast_text(i.filename),
                    cast_text(i.frame_ranges),
                )
                for i in items
            )
        )
        return

    if len(items) < 10:
        nuke.message(cast_str(html.replace("\n", "")))
    else:
        webbrowser.open(create_html_url(html))


def _on_script_load():
    show(find(iter_deep_all_nodes()))


def init_gui():
    wulifang.nuke.callback.on_script_load(_on_script_load)
