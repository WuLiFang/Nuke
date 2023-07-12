# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

from ._compat import text_type, binary_type


def cast_text(v):
    # type: (object) -> str
    if isinstance(v, text_type):
        return v
    if v is None:
        return ""
    if isinstance(v, binary_type):
        try:
            return v.decode("utf-8")
        except UnicodeDecodeError:
            return v.decode(sys.getfilesystemencoding())
    return text_type(v)
