# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any, Mapping, TypeVar, ValuesView

    T = TypeVar("T")


from ._compat import PY2


def itervalues(d):
    # type: (Mapping[Any, T]) -> ValuesView[T]
    if PY2:
        return d.itervalues()  # type: ignore
    return d.values()
