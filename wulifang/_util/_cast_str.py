# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from wulifang._compat.str import Str


from ._compat import PY2
from ._cast_binary import cast_binary
from ._cast_text import cast_text


def cast_str(v):
    # type: (object) -> Str
    if PY2:
        return cast_binary(v)  # type: ignore
    return cast_text(v)  # type: ignore
