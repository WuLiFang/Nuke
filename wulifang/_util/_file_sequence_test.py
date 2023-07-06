# -*- coding=UTF-8 -*-
# pyright: ignore, reportTypeCommentUsage=none

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


@pytest.mark.parametrize(
    ("paths", "expected"),
    [
        (("image.1.png", "image.2.png"), (("image.#.png", 1, 2),)),
        (("image.1.png", "image.2.png", "image.3.png"), (("image.#.png", 1, 3),)),
        (("example.txt",), (("example.txt", None, None),)),
        (("example_v1.txt",), (("example_v1.txt", None, None),)),
        (("image.0001.png", "image.0002.png"), (("image.####.png", 1, 2),)),
        (("image.0001.png", "image.0002.png"), (("image.####.png", 1, 2),)),
        (
            (
                "example.1001.exr",
                "example.1002.exr",
                "example.1003.exr",
            ),
            (
                (
                    "example.####.exr",
                    1001,
                    1003,
                ),
            ),
        ),
        (
            ("shot001/image.0001.png", "shot001/image.0002.png"),
            (("shot001/image.####.png", 1, 2),),
        ),
    ],
)
def test_from_paths(paths, expected):
    # type: (tuple[Text, ...], tuple[tuple[Text,Optional[int], Optional[int]], ...]) -> None
    got = list(FileSequence.from_paths(paths))
    assert len(got) == len(expected)
    for index in range(len(expected)):
        assert got[index].expr == expected[index][0]
        assert got[index].first == expected[index][1]
        assert got[index].last == expected[index][2]
