# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any, Text, Optional, Callable, TypeVar, ParamSpec

    T = TypeVar("T")
    P = ParamSpec("P")

from threading import Thread
from functools import wraps


def run_in_thread(
    name=None,
    daemon=None,
):
    # type: (Optional[Text],  Optional[bool]) -> Callable[[Callable[P, T]], Callable[P, Thread]]
    """Run func in thread."""

    def outer(f):
        # type: (Callable[P, T]) -> Callable[P, Thread]

        @wraps(f)
        def inner(*args, **kwargs):
            # type: (Any, Any) -> Thread
            thread = Thread(
                target=f,
                name=name,
                args=args,
                kwargs=kwargs,
            )
            if daemon:
                thread.daemon = True
            thread.start()
            return thread

        return inner  # type: ignore

    return outer
