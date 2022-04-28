# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import absolute_import, division, print_function, unicode_literals
import wulifang
from wulifang.infrastructure.logging_message_service import LoggingMessageService
from wulifang.infrastructure.multi_message_service import MultiMessageService


class _g:
    init_once = False


def init():
    if _g.init_once:
        return

    wulifang.message = MultiMessageService(
        wulifang.message,
        LoggingMessageService(),
    )

    _g.init_once = True
