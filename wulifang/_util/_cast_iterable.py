# -*- coding=UTF-8 -*-
# pyright: ignore, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


from wulifang.vendor.six.moves.collections_abc import Iterable

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Union, TypeVar

    T = TypeVar("T")

def cast_iterable(v):
    # type: (Union[T, Iterable[T], None]) -> Iterable[T]
    """Cast value to iterable, return empty iterable when value is none

    Args:
        v (typing.Any): value

    Returns:
        typing.Iterable: iterable that contains value
    """

    if v is None:
        return ()

    if isinstance(v, Iterable):
        return v

    return (v,)
