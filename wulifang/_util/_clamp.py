# -*- coding=UTF-8 -*-
# pyright: ignore

from __future__ import absolute_import, division, print_function, unicode_literals


def clamp(min, max, value):
    if value < min:
        return min
    if value > max:
        return max
    return value
