# -*- coding=UTF-8 -*-
# pyright: ignore, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import TypeVar, Iterable, Sequence, Iterator

    T = TypeVar("T")

def iter_chunk(input, size):
    # type: (Iterable[T], int) -> Iterator[Sequence[T]]
    b = [] # type: list[T]
    for i in input:
        b.append(i)
        if len(b) == size:
            yield b
            b = []
    if b:
        yield b
    return

