# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Mapping, TypeVar, ItemsView

    K = TypeVar("K")
    T = TypeVar("T")


from ._compat import PY2


def iteritems(d):
    # type: (Mapping[K, T]) -> ItemsView[K, T]
    if PY2:
        return d.iteritems()  # type: ignore
    return d.items()
