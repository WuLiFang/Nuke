# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any, Text, TypeVar, ParamSpec, Callable

    T = TypeVar("T")
    P = ParamSpec("P")


from functools import wraps

import nuke

from wulifang._util import cast_str


def undoable(name):
    # type: (Text) -> Callable[[(Callable[P, T])], Callable[P, T]]
    """(Decorator)add nuke undo group."""

    def outer(f):
        # type: (Callable[P, T]) -> Callable[P, T]
        @wraps(f)
        def inner(*args, **kwargs):
            # type: (Any, Any) -> T

            with nuke.Undo(cast_str(name)):
                return f(*args, **kwargs)  # type: ignore

        return inner  # type: ignore

    return outer
