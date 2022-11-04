# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any


def cast_int(v):
    # type: (Any) -> int
    if isinstance(v, int):
        return v
    return int(v)
