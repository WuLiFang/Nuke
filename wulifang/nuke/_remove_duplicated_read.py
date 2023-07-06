# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import webbrowser

import nuke

from wulifang._util import (
    cast_str,
    cast_text,
    create_html_url,
)
from wulifang.nuke._util import (
    undoable,
    Progress,
    create_node,
    replace_node,
    knob_of,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Iterable, Iterator


class ResultItem(object):
    def __init__(self, _node_fqn, _repl_node_fqn):
        # type: (Text, Text) -> None
        self.node_fqn = _node_fqn
        self.repl_node_fqn = _repl_node_fqn


def show(result):
    # type: (Iterable[ResultItem]) -> None

    result = list(result)
    if not result:
        nuke.message(cast_str("没有发现重复读取节点"))
        return

    webbrowser.open(create_html_url("\n".join(_html(result))))


def _html(result):
    # type: (Iterable[ResultItem]) -> ...
    yield """\
<style>
    td {
        padding: 8px;
    }
</style>"""
    yield "<h1>移除结果</h1>"
    yield """\
<table>
<tr>
    <th>名称</th>
    <th>替代为</th>
</tr>
"""
    for i in result:
        yield """\
            <tr>
                <td>%s</td>
                <td>%s</td>
            </tr>
""" % (
            i.node_fqn,
            i.repl_node_fqn,
        )
    yield "</table>"


class _DistinctReadNodes:
    def __init__(self):
        self.by_key = {}  # type: dict[Text, nuke.Node]

    def key(self, node):
        # type: (nuke.Node) -> Text
        return cast_text(node.writeKnobs(nuke.WRITE_NON_DEFAULT_ONLY | nuke.TO_VALUE))

    def match(self, node):
        # type: (nuke.Node) -> nuke.Node
        key = self.key(node)
        if key not in self.by_key:
            self.by_key[key] = node
        return self.by_key[key]


@undoable("移除重复的读取节点")
def remove():  # type: () -> Iterator[ResultItem]
    """Remove duplicated read to save memory."""

    nodes = nuke.allNodes(cast_str("Read"))

    distinct_read_nodes = _DistinctReadNodes()
    with Progress("移除重复的读取节点") as p:
        for index, n in enumerate(nodes):
            fqn = cast_text(n.fullName())
            p.set_message(fqn)
            p.set_value(float(index) / len(nodes))
            match = distinct_read_nodes.match(n)
            if match == n:
                continue

            dot = create_node(
                "Dot",
                inputs=(match,),
                label="代替: %s\n%s"
                % (
                    fqn,
                    cast_text(knob_of(n, "label", nuke.String_Knob).value()),
                ),
                hide_input=True,
                xpos=n.xpos() + 34,
                ypos=n.ypos() + 57,
            )
            replace_node(n, dot)
            nuke.delete(n)
            yield ResultItem(
                fqn,
                cast_text(match.fullName()),
            )
