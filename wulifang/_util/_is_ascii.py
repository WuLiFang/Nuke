# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

from ._cast_text import cast_text

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import AnyStr


def is_ascii(s):
    # type: (AnyStr) -> bool
    """Return true if @text can be convert to ascii.

    >>> is_ascii('a')
    True
    >>> is_ascii('测试')
    False

    """
    try:
        cast_text(s).encode("ascii")
        return True
    except (UnicodeEncodeError, UnicodeDecodeError):
        return False
