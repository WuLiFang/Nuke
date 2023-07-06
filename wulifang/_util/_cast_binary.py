# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

from ._cast_text import cast_text
from ._compat import binary_type


def cast_binary(v):
    # type: (object) -> bytes
    if isinstance(v, binary_type):
        return v
    if v is None:
        return b""
    return cast_text(v).encode("utf-8")
