# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Callable


class lazy_getter(object):
    def __init__(self, load):
        # type: (Callable[[], object]) -> None
        self._load = load
        self._value = None  # type: object
        self._once = False

    def reset(self):
        self._value = None
        self._once = False

    def __call__(self):
        if not self._once:
            self._value = self._load()
            self._once = True
        return self._value
