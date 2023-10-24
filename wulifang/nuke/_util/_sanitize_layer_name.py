# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text

import string

_CHAR = string.ascii_letters + string.digits + "-_"


def sanitize_layer_name(name):
    # type: (Text) -> Text
    # https://github.com/Psyop/Cryptomatte/blob/968d5e4b6171e29ba5f89d554117132a164e747e/nuke/cryptomatte_utilities.py#L691
    b = ""
    for i in name:
        if b == "" and i in string.digits:
            b += "_"
            b += i
        elif i in _CHAR:
            b += i
        else:
            b += "_"
    return b
