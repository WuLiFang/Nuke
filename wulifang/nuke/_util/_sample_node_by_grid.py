# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke

from wulifang.nuke._util import Progress
from wulifang._util import cast_str
from wulifang._compat.futures import ThreadPoolExecutor
from multiprocessing import Queue

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterator


def process_events():
    if not nuke.GUI:
        return
    from wulifang.vendor.Qt.QtCore import QCoreApplication

    QCoreApplication.processEvents()


def sample_node_by_grid(__node, grid=(100, 100)):
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
