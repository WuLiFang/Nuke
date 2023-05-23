# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional

from wulifang.vendor.pathlib2_unicode import PurePath
import sys


def is_local_file(path):
    # type: (Text) -> Optional[bool]
    if sys.platform == "win32":
        import ctypes

        return ctypes.windll.kernel32.GetDriveTypeW(PurePath(path).drive) == 3
