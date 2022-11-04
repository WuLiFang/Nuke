# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


from .._reload import reload as _raw_reload
import wulifang.license
import wulifang


class _g:
    init_once = False


def init():
    if _g.init_once:
        return
    try:
        wulifang.license.check()
    except wulifang.license.LicenseError:
        return

    _g.init_once = True


def reload():
    _raw_reload()
    init()
