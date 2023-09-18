# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang.nuke._util import create_node, knob_of, Progress, optional_knob_of
from wulifang._util import cast_str, cast_text
from collections import Counter
from wulifang._compat.futures import ThreadPoolExecutor
from multiprocessing import Queue

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterator, Text

_MIN_ALPHA = 0.5
_CHUNK_SIZE = 32


def _iter_color(__node, grid=(100, 100)):
    # type: (nuke.Node, tuple[int, int]) -> Iterator[tuple[float, float, float, float]]
    with Progress("颜色采样", 10) as p, ThreadPoolExecutor(32) as executor:
        index = 0
        queue = Queue()  # type: Queue[tuple[float, float, float, float]]
        job_count = 0

        def do(x, y):
            # type: (int, int) -> None
            queue.put(
                (
                    __node.sample(cast_str("red"), x, y),
                    __node.sample(cast_str("green"), x, y),
                    __node.sample(cast_str("blue"), x, y),
                    __node.sample(cast_str("alpha"), x, y),
                )
            )

        for x in range(0, __node.width(), max(1, int(__node.width() / grid[0]))):
            for y in range(0, __node.height(), max(1, int(__node.height() / grid[1]))):
                executor.submit(do, x, y)  # type: ignore
                job_count += 1

        while index < job_count:
            yield queue.get()
            index += 1
            p.set_value(index / job_count)


def _color_hex(color):
    # type: (tuple[float, float, float]) -> Text
    return "#%02X%02X%02X" % (
        round(color[0] * 255),
        round(color[1] * 255),
        round(color[2] * 255),
    )


def split(__node):
    # type: (nuke.Node) -> Iterator[nuke.Node]

    c = Counter(i for i in _iter_color(__node) if i[3] >= _MIN_ALPHA)
    if not c:
        nuke.message(cast_str("没有 alpha 大于 %.0f 的像素" % (_MIN_ALPHA)))
        return

    existing_color_hex = set()  # type: set[Text]
    for i in __node.dependent():
        if cast_text(i.name()).startswith("ColorKeyer"):
            color = optional_knob_of(i, "color", nuke.AColor_Knob)
            if color:
                v = color.value()
                if isinstance(v, float):
                    v = (v, v, v)
                existing_color_hex.add(_color_hex((v[0], v[1], v[2])))

    created_count = 0

    with Progress("创建节点") as p:
        for index, v in enumerate(c.most_common()):
            color = v[0]
            color_hex = _color_hex(color[:3])
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
