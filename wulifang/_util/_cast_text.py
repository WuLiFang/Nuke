# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

from ._compat import text_type, binary_type


def cast_text(v):
    # type: (object) -> str
    if isinstance(v, text_type):
        return v
    if v is None:
        return ""
    if isinstance(v, binary_type):
        return v.decode("utf-8")
    return text_type(v)
