# -*- coding=UTF-8 -*-
# pyright: strict
"""Windows ignore file.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import re

import nuke

import cast_unknown as cast
from ..core import HOOKIMPL

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, AnyStr, Optional


def is_ascii(text):
    # type: (AnyStr) -> bool
    """Return true if @text can be convert to ascii.

    >>> is_ascii('a')
    True
    >>> is_ascii('测试')
    False

    """
    try:
        _ = cast.binary(text, "ascii")
        return True
    except (UnicodeEncodeError, UnicodeDecodeError):
        return False


@HOOKIMPL
def is_ignore_filename(filename):
    # type: (Text) -> Optional[bool]
    ignore_pat = (r"thumbs\.db$", r".*\.lock$", r".* - 副本\b")
    basename = os.path.basename(filename)
    for pat in ignore_pat:
        if re.match(pat, basename, flags=re.I | re.U):
            return True
    if not is_ascii(filename):
        if filename.lower().endswith((".mov", ".mp4")):
            _ = nuke.createNode(
                b"StickyNote",
                (
                    "autolabel {{'<div align=\"center\">'+autolabel()+'</div>'}} "
                    "label {{{}\n\n"
                    '<span style="color:red;text-align:center;font-weight:bold">'
                    "mov,mp4格式使用非英文路径将可能导致崩溃</span>}}"
                )
                .format(filename)
                .encode("utf-8"),
                inpanel=False,
            )
            return True
        else:
            return nuke.ask(("使用非英文路径可能导致Nuke出错，忽略此文件？\n%s" % filename).encode("utf-8"))
    return None
