# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


def cast_int(v):
    # type: (object) -> int
    if isinstance(v, int):
        return v
    return int(v)  # type: ignore
