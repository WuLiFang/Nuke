# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text

import os


def force_rename(src, dst):
    # type: (Text, Text) -> None
    try:
        os.rename(src, dst)
    except FileExistsError:
        os.unlink(dst)
        os.rename(src, dst)
