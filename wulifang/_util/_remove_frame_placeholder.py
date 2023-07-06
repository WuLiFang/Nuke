# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import re

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


_PATTERN = re.compile(r"\W?(?:%0?\d*d|#+)\W?")


def remove_frame_placeholder(__s):
    # type: (Text) -> Text
    return _PATTERN.sub("", __s)
