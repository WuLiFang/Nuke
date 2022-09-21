# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Dict, Tuple, Iterator
    from .. import types

import os
import time
import wulifang
from wulifang.vendor.concurrent import futures
from wulifang.vendor import six

from wulifang import filename as fn


class FileService:
    def __init__(self):
        self._cache = dict()  # type: Dict[Text, Tuple[float, bool]]

    def exists(self, path, max_age=0):
        # type: (Text, float) -> bool
        max_age = max_age

        key = os.path.normcase(path)
        now = time.time()
        if key not in self._cache or self._cache[key][0] < now - max_age:
            try:
                stat = os.stat(path)
                if stat.st_size < 16 << 10:
                    wulifang.message.debug("small file: path=%s, size=%0.2fKiB" % (path, stat.st_size / (1 << 10)))
                self._cache[key] = (now, stat.st_size > 0)
            except OSError:
                self._cache[key] = (now, False)

        return self._cache[key][1]

    def missing_frames(self, filename, first, last, max_age=60):
        # type: (Text, int, int, float) -> Iterator[int]

        with futures.ThreadPoolExecutor(8) as executor:
            for f, is_exist in executor.map(
                lambda f: (f, self.exists(fn.expand_frame(filename, f), max_age)),
                six.moves.range(first, last + 1),
            ):
                if not is_exist:
                    yield f


def _(v):
    # type: (FileService) -> types.FileService
    return v
