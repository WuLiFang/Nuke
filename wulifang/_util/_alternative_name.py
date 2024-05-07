# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def alternative_name(s):
    # type: (Text) -> Text
    index = s.rfind("~")
    if index < 0:
        return s + "~"
    try:
        if index == len(s)-1:
            return s + "1"
        return "%s~%d" % (s[:index], int(s[index + 1 :])+1)
    except ValueError:
        return s + "~"
