# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text

import re

_PATTERN = re.compile(r"^(.*?)(?: ([-\d, ]+))?$")


class File(object):
    def __init__(self, __raw):
        # type: (Text) -> None
        self._raw = __raw
        match = _PATTERN.match(__raw)
        self._name = ""
        self._range = ""
        if match:
            for index, i in enumerate(match.groups()):
                if index == 0:
                    self._name = i
                elif index == 1:
                    self._range = i

    def raw(self):
        return self._raw

    def name(self):
        return self._name

    def range(self):
        return self._range


def parse_file_input(__s):
    # type: (Text) -> File
    return File(__s)
