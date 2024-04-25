# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

from ._compat import text_type, binary_type


_POSSIBLE_ENCODING = (
    "utf-8",
    sys.getdefaultencoding(),
    sys.getfilesystemencoding(),
    "gbk",
)


def cast_text(v):
    # type: (object) -> str
    if isinstance(v, text_type):
        return v
    if v is None:
        return ""
    if isinstance(v, binary_type):
        for i in _POSSIBLE_ENCODING:
            try:
                return v.decode(i)
            except UnicodeDecodeError:
                pass
    return text_type(v)
