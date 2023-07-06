# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


def cast_float(v):
    # type: (object) -> float
    if isinstance(v, float):
        return v
    return float(v)  # type: ignore
