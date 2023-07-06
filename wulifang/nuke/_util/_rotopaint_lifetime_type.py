# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


# see _rotopaint.FrameRangeType
class RotopaintLifeTimeType:
    ALL = 0
    START_TO_FRAME = 1
    SINGLE_FRAME = 2
    FRAME_TO_END = 3
    RANGE = 4
