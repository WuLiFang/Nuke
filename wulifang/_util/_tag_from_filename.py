# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

from wulifang.vendor.wlf import path as wlf_path

import os.path

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def tag_from_filename(_filename):
    # type: (Text) -> Text
    """The footage tag name.

    >>> tag_from_filename('Z:/MT/Render/image/MT_BG_co/MT_BG_co_PuzzleMatte1/PuzzleMatte1.001.exr')
    u'PuzzleMatte1'
    """

    basename = os.path.basename(_filename)
    if "__" in _filename:
        return basename.split("__")[-1]

    # TODO: avoid use of library
    return wlf_path.PurePath(_filename).tag  # type: ignore
