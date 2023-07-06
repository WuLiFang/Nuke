# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import webbrowser
import os

import nuke
from wulifang._util import (
    cast_iterable,
    cast_str,
    cast_text,
)
from wulifang.nuke._util import (
    Progress,
    knob_of,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Union, Optional, Iterable


def render(_nodes, frame=None, open_dir=False):
    # type: (Union[Iterable[nuke.Node], nuke.Node], Optional[int], bool) -> None
    """create png for given @nodes."""

    project_dir = cast_text(nuke.value(cast_str("root.project_directory")))

    if not project_dir:
        nuke.message(cast_str("未设置工程目录"))
        return

    script_name = os.path.join(
        os.path.splitext(
            os.path.basename(cast_text(nuke.value(cast_str("root.name"))))
        )[0]
    )
    if frame is None:
        frame = nuke.frame()
    with Progress("渲染PNG") as p:
        for n in cast_iterable(_nodes):
            p.increase()
            if n.hasError() or knob_of(n, "disable", nuke.Boolean_Knob).value():
                continue
            node_fqn = cast_text(n.fullName())
            p.set_message(node_fqn)
            n = nuke.nodes.Write(inputs=[n], channels=cast_str("rgba"))
            knob_of(n, "file", nuke.File_Knob).fromUserText(
                cast_str("%s/%s.%s.png" % (script_name, node_fqn, frame))
            )
            nuke.execute(n, frame, frame)

            nuke.delete(n)
    if open_dir:
        webbrowser.open(
            os.path.join(
                project_dir,
                script_name,
            )
        )
