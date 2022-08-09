# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import List, Callable, Text

import nuke
from wulifang.infrastructure.exception_as_message import exception_as_message


class CleanupService:
    def __init__(self, key="_WULIFANG_CLEANUP"):
        # type: (Text) -> None
        self._key = key

    def _cleanups(self):
        # type: () -> List[Callable[[],None]]
        cleanups = getattr(nuke, self._key, None)
        if cleanups is None:
            setattr(nuke, self._key, [])
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
            with exception_as_message():
                cleanups.pop()()
