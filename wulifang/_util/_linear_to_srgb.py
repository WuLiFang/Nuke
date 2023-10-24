# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


def linear_to_srgb(__v):
    # type: (float) -> float
    # https://www.nayuki.io/res/srgb-transform-library/srgbtransform.py
    if __v <= 0.0:
        return 0.0
    elif __v >= 1:
        return 1.0
    elif __v < 0.0031308:
        return __v * 12.92
    else:
        return __v ** (1 / 2.4) * 1.055 - 0.055
