# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any

from ._cast_text import cast_text
from ._compat import binary_type


def cast_binary(v):
    # type: (Any) -> bytes
    if isinstance(v, binary_type):
        return v
    return cast_text(v).encode("utf-8")
