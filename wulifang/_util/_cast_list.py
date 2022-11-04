# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any, List

import sys

_py2 = sys.version_info[0] == 2


if _py2:
    _text_type = unicode  # type: ignore
    _binary_type = str  # type: ignore
else:
    _text_type = str
    _binary_type = bytes


def cast_list(v):
    # type: (Any) -> List[Any]
    if v is None:
        return []
    if isinstance(v, list):
        return v  # type: ignore
    if isinstance(v, tuple):
        return list(v)  # type: ignore
    return [v]
