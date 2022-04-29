# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import absolute_import, division, print_function, unicode_literals


import wulifang
import wulifang.nuke
from wulifang.infrastructure.logging_message_service import LoggingMessageService
from wulifang.infrastructure.multi_message_service import MultiMessageService
from wulifang.nuke.infrastructure.callback_service import CallbackService
from wulifang.nuke.infrastructure.active_viewer_service import ActiveViewerService
from wulifang.nuke.infrastructure.cleanup_service import CleanupService


class _g:
    init_once = False


def init():
    if _g.init_once:
        return

    wulifang.nuke.cleanup = CleanupService()
    wulifang.nuke.cleanup.run()
    wulifang.message = MultiMessageService(
        wulifang.message,
        LoggingMessageService(),
    )
    wulifang.nuke.active_viewer = ActiveViewerService()
    wulifang.nuke.callback = CallbackService()
    wulifang.nuke.callback.on_script_load(lambda: wulifang.publish.validate())
    wulifang.nuke.callback.on_script_save(lambda: wulifang.publish.request_validate())
    wulifang.nuke.callback.on_script_close(lambda: wulifang.publish.publish())

    _g.init_once = True
