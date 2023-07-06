# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import wulifang

def init():
    import sys

    if sys.platform != "win32":
        return
    from wulifang.vendor import win_unicode_console

    win_unicode_console.enable()

    wulifang.cleanup.add(win_unicode_console.disable)
