# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any


from ._compat import text_type, binary_type


def cast_text(v):
    # type: (Any) -> str
    if isinstance(v, binary_type):
        return v.decode("utf-8")
    if isinstance(v, text_type):
        return v
    return text_type(v)
