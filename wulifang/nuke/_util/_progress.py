# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import time
import math
import gc

import nuke
from wulifang._util import cast_str

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional, TypeVar

    T = TypeVar("T")


class Progress:
    class Cancelled(RuntimeError):
        def __init__(self):
            RuntimeError.__init__(self, "cancelled")

    def __init__(
        self,
        __name,  # type: Text
        estimate_secs=5.0,  # type: float
    ):
        self.__task = nuke.ProgressTask(cast_str(__name))
        self._value = 0.0
        self._start_at = time.time()
        self._last_update_at = 0
        self._estimate_secs = max(0.001, estimate_secs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # type: (Optional[type], Optional[Exception], Optional[object]) -> bool
        del self.__task
        gc.collect()  # required to avoid hanging progress on error
        return isinstance(exc_value, Progress.Cancelled)

    def set_message(
        self,
        s,  # type: Text
    ):
        self._must_not_cancelled()
        self.__task.setMessage(cast_str(s))

    def value(self):
        "[0.0, 1.0]"
        return self._value

    def set_value(self, v):
        # type: (float) -> None
        "[0.0, 1.0]"
        self._must_not_cancelled()
        if v == self._value:
            return
        assert 0.0 <= v <= 1.0, "progress value should in range [0.0, 1.0]"
        self._value = v
        self.__task.setProgress(int(self._value * 100))
        self._last_update_at = time.time()

    def elapsed_secs(self):
        return time.time() - self._start_at

    def _estimate_value(self):
        # type: () -> float
        v = 1.0 - math.exp(-self.elapsed_secs() / self._estimate_secs)
        if v > 0.99:
            self._estimate_secs *= 2
            return self._estimate_value()
        return v

    def increase(self, delta=None):
        # type: (Optional[float]) -> None
        # print("increase", self._value, delta, self._estnimate_value())
        if delta is None:
            self.set_value(self._estimate_value())
            return

        self.set_value(self.value() + delta)

    def _is_cancelled(self):
        return self.__task.isCancelled()

    def _must_not_cancelled(self):
        if self._is_cancelled():
            raise Progress.Cancelled()
            
