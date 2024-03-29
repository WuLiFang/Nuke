# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


import os
import shutil

from wulifang._util import cast_text
import wulifang


def copy_file(src, dst):
    # type: (Text, Text) -> Text
    src = cast_text(src)
    dst = cast_text(dst)
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(dst))
    wulifang.message.debug("copy:\n\t\t%s\n\t->\t%s" % (src, dst))
    try:
        return shutil.copy2(src, dst)
    except shutil.Error:
        return dst
