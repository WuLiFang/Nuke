# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import time

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def format_time(unix_secs):
    # type: (float) -> Text
    return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(unix_secs))
