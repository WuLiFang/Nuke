# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any, Mapping, TypeVar, ItemsView

    T = TypeVar("T")


from ._compat import PY2


def iteritems(d):
    # type: (Mapping[T, Any]) -> ItemsView[T, Any]
    if PY2:
        return d.iteritems()  # type: ignore
    return d.items()
