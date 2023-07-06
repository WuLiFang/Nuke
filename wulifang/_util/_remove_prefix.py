# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def remove_prefix(__s, __prefix):
    # type: (Text,Text) -> Text
    if __s.startswith(__prefix):
        return __s[len(__prefix) :]
    return __s
