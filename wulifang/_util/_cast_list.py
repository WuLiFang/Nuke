# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import List, TypeVar, Union

    T = TypeVar("T")


def cast_list(v):
    # type: (Union[T, list[T], tuple[T]]) -> List[T]
    if v is None:
        return []
    if isinstance(v, list):
        return v  # type: ignore
    if isinstance(v, tuple):
        return list(v)  # type: ignore
    return [v]
