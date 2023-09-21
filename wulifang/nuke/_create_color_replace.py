# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang.nuke._util import (
    create_node,
    knob_of,
    Progress,
    optional_knob_of,
    sample_node_by_grid,
)
from wulifang._util import cast_str, cast_text, hex_color, iter_chunk
from wulifang.vendor.six.moves import range
from collections import Counter
import math

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterator, Text

_MIN_ALPHA = 0.5


def create(__node):
    # type: (nuke.Node) -> Iterator[nuke.Node]

    c = Counter(i for i in sample_node_by_grid(__node) if i[3] >= _MIN_ALPHA)
    if not c:
        nuke.message(cast_str("没有 alpha 大于 %.0f 的像素" % (_MIN_ALPHA)))
        return

    existing_color_hex = set()  # type: set[Text]
    for i in __node.dependent():
        if cast_text(i.name()).startswith("ColorReplace"):
            for node_index in range(16):
                src = optional_knob_of(i, "src%d" % (node_index + 1), nuke.Color_Knob)
                if src:
                    v = src.array()
                    existing_color_hex.add(hex_color(v))

    total_chunk = math.ceil(len(c) / 16.0)
    with Progress("创建节点") as p:
        for node_index, colors in enumerate(
            iter_chunk(
                (
                    i
                    for i, _ in c.most_common()
                    if hex_color(i[:3]) not in existing_color_hex
                ),
                16,
            )
        ):
            if node_index > 0 and not nuke.ask(
                cast_str("已经创建了 %d 个节点，继续？" % (node_index,))
            ):
                return

            p.set_message(" ".join(hex_color(i) for i in colors))
            p.set_value(node_index / total_chunk)

            n = create_node(
                "ColorReplace",
                inputs=(__node,),
            )
            for node_index, src in enumerate(colors):
                knob_of(n, "src%d" % (node_index + 1), nuke.Color_Knob).setValue(
                    src[:3]
                )

            yield n
