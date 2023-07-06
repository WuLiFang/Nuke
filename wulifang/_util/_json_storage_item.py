# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import wulifang
import json

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Callable


class JSONStorageItem(object):
    def __init__(self, _key, _default):
        # type: (Text, Callable[[], object]) -> None
        self._storage = wulifang.local_storage
        self._key = _key
        self._default = _default
        self._value = None  # Type: Optional[object]

    def _get(self):
        # type: () -> object
        s = self._storage[self._key]
        if not s:
            return self._default()
        return json.loads(s)

    def invalidate_cache(self):
        # type: () -> None
        self._value = None

    def get(self):
        # type: () -> object
        if self._value is None:
            self._value = self._get()
        return self._value

    def set(self, value):
        # type: (object) -> None
        if value is None:
            del self._storage[self._key]
            return
        s = json.dumps(value)
        self._storage[self._key] = s
        self.invalidate_cache()
