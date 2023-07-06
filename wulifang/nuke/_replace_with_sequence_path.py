# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import re
import webbrowser

import nuke

from wulifang._util import (
    cast_str,
    cast_text,
    iteritems,
    create_html_url,
)
from wulifang.nuke._util import (
    knob_of,
    wlf_write_node,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Iterable, Optional, Iterator


class ResultItem:
    def __init__(self, knob_fqn, old_filename, new_filename, frame):
        # type: (Text, Text, Text, int) -> None
        self.knob_fqn = knob_fqn
        self.old_value = old_filename
        self.new_value = new_filename
        self.frame = frame


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
    <th>帧匹配</th>
</tr>
"""
    for i in result:
        yield """\
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%d</td>
            </tr>
""" % (
            i.knob_fqn,
            i.old_value,
            i.new_value,
            i.frame,
        )
    yield "</table>"


def show(result):
    # type: (Iterable[ResultItem]) -> None

    result = list(result)
    if not result:
        nuke.message(cast_str("没有发现需要替换的文件"))
        return

    webbrowser.open(create_html_url("\n".join(_html(result))))


def _replace_knob(k):
    # type: (nuke.File_Knob) -> Iterator[ResultItem]
    old_value = cast_text(k.value())
    if not old_value:
        return

    class local:
        frame = None  # type: Optional[int]

    def repl(match):
        # type: (re.Match[Text]) -> Text
        local.frame = int(match.group(1))
        return r".%0{}d.".format(len(match.group(1)))

    new_value = re.sub(
        r"\.([\d]+)\.",
        repl,
        old_value,
    )
    if local.frame is None:
        return

    k.fromUserText(cast_str(new_value))
    yield ResultItem(
        cast_text(k.fullyQualifiedName()),
        old_value,
        new_value,
        local.frame,
    )


def replace(nodes):
    # type: (Iterable[nuke.Node]) -> Iterator[ResultItem]

    root = nuke.root()

    flag_frame = None  # type: Optional[int]

    for n in nodes:
        for _, k in iteritems(n.knobs()):
            if isinstance(k, nuke.File_Knob):
                for i in _replace_knob(k):
                    flag_frame = i.frame
                    yield i

    n = wlf_write_node()
    if n:
        if flag_frame:
            flag_frame = int(flag_frame)
            root.setFrame(flag_frame)
            knob_of(n, "custom_frame", nuke.Array_Knob).setValue(flag_frame)
            knob_of(n, "use_custom_frame", nuke.Boolean_Knob).setValue(True)
