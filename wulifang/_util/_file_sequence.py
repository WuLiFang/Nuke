# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional, Iterable

import re
from wulifang.vendor.six.moves import xrange


def _iter_possible_frames(s):
    # type: (Text) -> Iterable[int]
    for start in xrange(len(s)):
        for end in xrange(start + 1, len(s) + 1):
            yield int(s[start:end])


class FileSequence(object):
    _frame_placeholder_pattern = re.compile(r"%0?\d*d|#+")
    _frame_value_pattern = re.compile(r"\d+")

    def __init__(self, expr, first=None, last=None):
        # type: (Text, Optional[int], Optional[int]) -> None
        self.expr = expr
        self.first = first
        self.last = last

    def __str__(self):
        return "FileSequence<expr='%s'%s%s>" % (
            self.expr,
            "" if self.first is None else " first=%d" % self.first,
            "" if self.last is None else " last=%d" % self.last,
        )

    __repr__ = __str__
    __unicode__ = __str__

    def include_frame(self, frame):
        # type: (int) -> bool
        if self.first != None and self.first > frame:
            return False
        if self.last != None and self.last < frame:
            return False
        return True

    def __contains__(self, name):
        # type: (Text) -> bool
        if name == self.expr:
            return True
        for match in self._frame_value_pattern.finditer(name):
            for frame in _iter_possible_frames(match.group(0)):
                if not self.include_frame(frame):
                    continue
                if self.expand_frame(self.expr, frame) == name:
                    return True
        return False

    @classmethod
    def expand_frame(cls, expr, frame):
        # type: (Text, int) -> Text

        def repl(match):
            # type: (re.Match[Text]) -> Text
            m = match.group(0)
            if m == "#" * len(m):
                return ("%d" % (frame,)).rjust(len(m), "0")

            return m % (frame,)

        return cls._frame_placeholder_pattern.sub(repl, expr)
