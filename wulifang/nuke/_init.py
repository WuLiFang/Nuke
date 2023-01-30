# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false
from __future__ import absolute_import, division, print_function, unicode_literals

import wulifang
import wulifang.license
import wulifang.nuke
from wulifang.infrastructure.multi_message_service import MultiMessageService
from wulifang.nuke.infrastructure.active_viewer_service import ActiveViewerService
from wulifang.nuke.infrastructure.callback_service import CallbackService
from wulifang.nuke.infrastructure.manifest_service import ManifestService

import nuke
from . import _preference


class _g:
    init_once = False
    skip_gui = False


def skip_gui():
    return _g.skip_gui


def init():
    if _g.init_once:
        return
    wulifang.manifest = ManifestService()
    if nuke.GUI:
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
    nuke.pluginAddPath("../../../lib".encode("utf-8"))
    nuke.pluginAddPath("../../../plugins".encode("utf-8"))
    wulifang.cleanup.run()

    wulifang.nuke.active_viewer = ActiveViewerService()
    wulifang.nuke.callback = CallbackService()
    wulifang.nuke.callback.on_script_load(lambda: wulifang.publish.validate())
    wulifang.nuke.callback.on_script_save(lambda: wulifang.publish.request_validate())

    def _on_script_close():
        if not nuke.value(b"root.name"):
            return
        wulifang.publish.publish()

    wulifang.nuke.callback.on_script_close(_on_script_close)
    _preference.init()
    _g.init_once = True
