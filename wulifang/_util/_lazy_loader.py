# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Callable


class LazyLoader(object):
    def __init__(self, load):
        # type: (Callable[[], object]) -> None
        self._load = load
        self._value = None  # type: object

    def reset(self):
        self._value = None

    def get(self):
        if self._value is None:
            self._value = self._load()
        return self._value
