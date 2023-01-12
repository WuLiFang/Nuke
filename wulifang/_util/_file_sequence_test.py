# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional

import pytest


from ._file_sequence import FileSequence


@pytest.mark.parametrize(
    ("expr", "frame", "expected"),
    [
        ("", 0, ""),
        ("test.txt", 0, "test.txt"),
        ("image.%d.jpg", 123, "image.123.jpg"),
        ("image.%04d.jpg", 123, "image.0123.jpg"),
        ("image.#.jpg", 123, "image.123.jpg"),
        ("image.####.jpg", 123, "image.0123.jpg"),
    ],
)
def test_expand_frame(expr, frame, expected):
    # type: (Text, int, Text) -> None
    assert FileSequence.expand_frame(expr, frame) == expected


@pytest.mark.parametrize(
    ("expr", "first", "last", "item", "expected"),
    [
        ("test.txt", None, None, "test.txt", True),
        ("", None, None, "test.txt", False),
        ("%d.jpg", None, None, "1.jpg", True),
        ("%d.jpg", 0, 100, "1.jpg", True),
        ("%d.jpg", 0, 100, "1.png", False),
        ("%d.jpg", 0, 100, "101.jpg", False),
        ("%d.jpg", 0, 100, "01.jpg", False),
        ("%02d.jpg", 0, 100, "01.jpg", True),
        ("test_v1.%02d.jpg", 0, 100, "test_v1.01.jpg", True),
        ("%d.jpg", None, None, "1001.jpg", True),
        ("123%02d.jpg", 4, 4, "12304.jpg", True),
        ("123%02d.jpg", 5, 5, "12304.jpg", False),
        ("%02d123.jpg", 4, 4, "04123.jpg", True),
        ("1%02d2.jpg", 4, 4, "1042.jpg", True),
    ],
)
def test_contains(expr, first, last, item, expected):
    # type: (Text, Optional[int], Optional[int], Text, bool) -> None
    assert (item in FileSequence(expr, first, last)) == expected
