# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any


import sys
import wulifang
import nuke
from wulifang._util import cast_str


def init_gui():
    if sys.version_info.major == 2:
        return

    raw_hook = sys.excepthook

    def hook(type, value, traceback):
        # type: (type[BaseException], BaseException, Any) -> None
        if raw_hook:  # type: ignore
            raw_hook(type, value, traceback)
        if (
            isinstance(value, NameError)
            and value.args == ("name 'unicode' is not defined",)
            and nuke.value(cast_str("root.name"), cast_str(""))
        ):
            wulifang.message.info(
                "脚本出错，python 版本不兼容。当前工程需使用 Nuke12 以下版本。"
            )

    def cleanup():
        if sys.excepthook == hook:
            sys.excepthook = raw_hook

    sys.excepthook = hook
    wulifang.cleanup.add(cleanup)
