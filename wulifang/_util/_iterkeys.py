# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any, Mapping, TypeVar, KeysView

    T = TypeVar("T")


from ._compat import PY2


def iterkeys(d):
    # type: (Mapping[T, Any]) -> KeysView[T]
    if PY2:
        return d.iterkeys()  # type: ignore
    return d.keys()
