# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional, Iterable, Iterator

import re
from wulifang.vendor.six.moves import xrange
import os
from ._iteritems import iteritems


def _iter_possible_frames(s):
    # type: (Text) -> Iterable[int]
    for start in xrange(len(s)):
        for end in xrange(start + 1, len(s) + 1):
            yield int(s[start:end])


def _iter_possible_frame_placeholder(s):
    # type: (Text) -> Text
    if s.startswith("0"):
        yield "%%0%dd" % (len(s),)
        yield "#" * len(s)
        return

    yield "%d"
    yield "#"
    for i in range(2, len(s) + 1):
        yield "%%%dd" % (i,)
        yield "%%0%dd" % (i,)
        yield "#" * i


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

    @classmethod
    def from_paths(cls, paths, frame_count_gt=0):
        # type: (Iterable[Text], int) -> Iterator[FileSequence]
        m = {}  # type: dict[Text, set[int]]
        for path in paths:
            dirname, basename = os.path.split(path)
            if path not in m:
                m[path] = set()
            for match in cls._frame_value_pattern.finditer(basename):
                frame_text = match.group(0)
                frame = int(frame_text)
                for placeholder in _iter_possible_frame_placeholder(frame_text):
                    key = os.path.join(
                        dirname,
                        "%s%s%s"
                        % (
                            basename[: match.start(0)],
                            placeholder,
                            basename[match.end(0) :],
                        ),
                    ).replace("\\", "/")
                    if key not in m:
                        m[key] = set()
                    m[key].add(frame)

        used_path = set()  # type: set[Text]

        for k, v in sorted(iteritems(m), key=lambda x: (len(x[1]) == 1, -len(x[1]), "#" not in x[0], x[0])):  # type: ignore
            k = k  # type: Text
            v = v  # type: set[int]
            if len(v) == 0 and k not in used_path:
                yield FileSequence(k)
                used_path.add(k)
                continue

            frame_count = 0
            for frame in v:
                path = FileSequence.expand_frame(k, frame)
                if path in used_path:
                    continue
                frame_count += 1
                used_path.add(path)

            if frame_count > frame_count_gt:
                yield FileSequence(k, min(v), max(v))
