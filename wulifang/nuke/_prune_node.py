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
    replace_node,
    Progress,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Iterable, Iterator


class ResultItem(object):
    ACTION_DELETE = "删除"
    ACTION_DETACH = "分离"

    def __init__(self, node_fqn, action, reason):
        # type: (Text, Text, Text) -> None
        self.node_fqn = node_fqn
        self.action = action
        self.reason = reason


def _html(result):
    # type: (Iterable[ResultItem]) -> ...
    yield """\
<style>
    td {
        padding: 8px;
    }
</style>"""
    yield "<h1>清理结果</h1>"
    yield """\
<table>
<tr>
    <th>名称</th>
    <th>操作</th>
    <th>原因</th>
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
            i.node_fqn,
            i.action,
            i.reason,
        )
    yield "</table>"


def show(result):
    # type: (Iterable[ResultItem]) -> None

    result = list(result)
    if not result:
        nuke.message(cast_str("没有发现无用节点"))
        return

    webbrowser.open(create_html_url("\n".join(_html(result))))


@undoable("清理无用节点")
def prune(
    nodes,  # type: Iterable[nuke.Node]
):
    # type: (...) -> Iterator[ResultItem]

    with Progress("清理无用节点") as p:
        p.set_message("列出所有节点...")
        nodes = sorted(nodes, key=lambda n: (n.ypos(), n.xpos()), reverse=True)

        for n in nodes:
            p.set_message(
                "1/2: %s" % (cast_text(n.fullName())),
            )
            p.increase()
            if _is_disabled_and_no_expression(n):
                yield ResultItem(
                    cast_text(n.fullName()), ResultItem.ACTION_DETACH, "禁用且无表达式输出"
                )
                replace_node(n, n.input(0))
                nodes.remove(n)

        in_use_nodes = _InUseNodes()
        for n in nodes:
            p.set_message(
                "2/2: %s" % (cast_text(n.fullName())),
            )
            p.increase()
            if not in_use_nodes.has(n):
                yield ResultItem(
                    cast_text(n.fullName()), ResultItem.ACTION_DELETE, "输出未被使用"
                )
                nuke.delete(n)


def _is_disabled_and_no_expression(n):
    # type: (nuke.Node) -> bool
    k = n.knob(cast_str("disable"))
    if not k:
        return False
    return bool(
        k.value() and not k.hasExpression() and not n.dependent(nuke.EXPRESSIONS)
    )


class _InUseNodes(object):
    def __init__(self):
        self.by_fqn = {}  # type: dict[str, bool]

    def has(self, n):
        # type: (nuke.Node) -> bool
        fqn = cast_text(n.fullName())
        if fqn not in self.by_fqn:
            name = cast_text(n.fullName())
            if (
                name.startswith("_")
                or name == "VIEWER_INPUT"
                or cast_text(n.Class())
                in (
                    "BackdropNode",
                    "Read",
                    "Write",
                    "Viewer",
                    "GenerateLUT",
                    "wlf_Write",
                )
            ):
                self.by_fqn[fqn] = True
            else:
                self.by_fqn[fqn] = not _is_disabled_and_no_expression(n) and any(
                    self.has(i) for i in n.dependent()
                )

        return self.by_fqn[fqn]
