# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import List, Callable, Text
    from wulifang.types.cleanup_service import CleanupService as Service

from wulifang._util import capture_exception
import wulifang.vendor


class CleanupService:
    def __init__(self, key="_WULIFANG_CLEANUP"):
        # type: (Text) -> None
        self._key = key

    def _cleanups(self):
        # type: () -> List[Callable[[],None]]
        cleanups = getattr(wulifang.vendor, self._key, None)
        if cleanups is None:
            setattr(wulifang.vendor, self._key, [])
            return self._cleanups()
        return cleanups

    def add(self, cb):
        # type: (Callable[[], None]) -> Callable[[], None]

        s = self._cleanups()
        s.append(cb)

        def _cancel():
            try:
                s.remove(cb)
            except ValueError:
                pass

        return _cancel

    def run(self):
        cleanups = self._cleanups()
        while cleanups:
            with capture_exception():
                cleanups.pop()()


def _(v):
    # type: (CleanupService) -> Service
    return v
