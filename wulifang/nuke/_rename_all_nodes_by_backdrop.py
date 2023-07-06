# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang._util import cast_str, assert_isinstance, cast_text


def rename_all_nodes_by_backdrop():
    """Rename all nodes by them belonged backdrop node ."""

    for backdrop in nuke.allNodes(cast_str("BackdropNode")):
        nodes = assert_isinstance(backdrop, nuke.BackdropNode).getNodes()
        title = (
            cast_text(backdrop[cast_str("label")].value())
            .split(("\n"))[0]
            .split((" "))[0]
        )
        if not title:
            continue
        for node in nodes:
            if "_" in cast_text(node.name()) or (
                nuke.exists(cast_str(cast_text(node.name()) + ".disable"))
                and node[cast_str("disable")].value()
            ):
                continue
            if cast_text(node.Class()) == "Group":
                name = cast_text(node.name()).rstrip("0123456789")
                node.setName(
                    cast_str("%s_%s_1" % (name, title)), updateExpressions=True
                )
            else:
                node.setName(
                    cast_str("%s_%s_1" % (cast_text(node.Class()), title)),
                    updateExpressions=True,
                )
