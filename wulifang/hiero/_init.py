# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import hiero.core

from . import _win_unicode_console
from .._reload import reload as _raw_reload
import wulifang.license
import wulifang
from ..infrastructure.multi_message_service import MultiMessageService
from wulifang import _sentry


class _g:
    init_once = False
    skip_gui = False


def skip_gui():
    return _g.skip_gui


def init():
    if _g.init_once:
        return
    if hiero.core.GUI:
        from wulifang.infrastructure.tray_message_service import TrayMessageService

        wulifang.message = MultiMessageService(
            wulifang.message,
            TrayMessageService(),
        )
    try:
        wulifang.license.check()
    except wulifang.license.LicenseError:
        _g.skip_gui = True
        return

    wulifang.cleanup.run()
    _sentry.init()
    _win_unicode_console.init()
    _g.init_once = True


def reload():
    _raw_reload()
    init()
