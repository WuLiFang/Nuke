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
from wulifang._util import cast_str, cast_text, hex_color
from collections import Counter

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterator, Text

_MIN_ALPHA = 0.5
_CHUNK_SIZE = 32



def split(__node):
    # type: (nuke.Node) -> Iterator[nuke.Node]

    c = Counter(i for i in sample_node_by_grid(__node) if i[3] >= _MIN_ALPHA)
    if not c:
        nuke.message(cast_str("没有 alpha 大于 %.0f 的像素" % (_MIN_ALPHA)))
        return

    existing_color_hex = set()  # type: set[Text]
    for i in __node.dependent():
        if cast_text(i.name()).startswith("ColorKeyer"):
            color = optional_knob_of(i, "color", nuke.AColor_Knob)
            if color:
                v = color.array()
                existing_color_hex.add(hex_color(v[:3]))

    created_count = 0

    with Progress("创建节点") as p:
        for index, v in enumerate(c.most_common()):
            color = v[0]
            color_hex = hex_color(color[:3])
            p.set_message(color_hex)
            p.set_value(index / len(c))

            # skip existing color
            if color_hex in existing_color_hex:
                continue
            existing_color_hex.add(color_hex)

            n = create_node(
                "ColorKeyer2",
                inputs=(__node,),
            )
            created_count += 1
            knob_of(n, "color", nuke.AColor_Knob).setValue(
                color,
            )
            yield n
            if created_count % _CHUNK_SIZE == 0 and not nuke.ask(
                cast_str("已经创建了 %d 个节点，继续？" % (created_count,))
            ):
                return
