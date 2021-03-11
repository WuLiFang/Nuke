# -*- coding=UTF-8 -*-
"""tests for asset.missing_frames.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import random

import cast_unknown as cast
import six
from pathlib2_unicode import Path

from asset import missing_frames


def test_exists_simple():
    assert missing_frames.exists("NOT_EXISTED") is False
    assert len(missing_frames._EXISTS_CACHE) == 1
    assert missing_frames.exists("NOT_EXISTED", ttl=100) is False
    assert len(missing_frames._EXISTS_CACHE) == 1

    assert missing_frames.exists(__file__) is True
    assert len(missing_frames._EXISTS_CACHE) == 2
    assert missing_frames.exists(__file__, ttl=100) is True
    assert len(missing_frames._EXISTS_CACHE) == 2


def test_get_not_existed():
    assert missing_frames.get("NOT_EXISTED", 1, 100) == list(range(1, 101))


def test_get_not_missing(tmpdir):
    filename = cast.text(tmpdir / ('test.%04d.exr'))
    for i in six.moves.range(1, 101):
        Path(filename % i).write_text("")

    assert missing_frames.get(filename, 1, 100) == []


def test_get_missing_middle(tmpdir):
    filename = cast.text(tmpdir / ('test.%04d.exr'))
    expected = [4, 5, 6, 7, 8, 9, 10]
    for i in six.moves.range(1, 101):
        if i in expected:
            continue
        Path(filename % i).write_text("")

    assert missing_frames.get(filename, 1, 100) == expected


def test_get_missing_start(tmpdir):
    filename = cast.text(tmpdir / ('test.%04d.exr'))
    expected = [1, 2, 3, 4, 5]
    for i in six.moves.range(1, 101):
        if i in expected:
            continue
        Path(filename % i).write_text("")

    assert missing_frames.get(filename, 1, 100) == expected


def test_get_missing_end(tmpdir):
    filename = cast.text(tmpdir / ('test.%04d.exr'))
    expected = [95, 96, 97, 98]
    for i in six.moves.range(1, 101):
        if i in expected:
            continue
        Path(filename % i).write_text("")

    assert missing_frames.get(filename, 1, 100) == expected


def test_get_missing_random(tmpdir):
    filename = cast.text(tmpdir / ('test.%04d.exr'))
    expected = sorted(random.sample(range(1, 101), 50))
    for i in six.moves.range(1, 101):
        if i in expected:
            continue
        Path(filename % i).write_text("")

    assert missing_frames.get(filename, 1, 100) == expected
