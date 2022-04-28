# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import absolute_import, division, print_function, unicode_literals


import wulifang
from wulifang.infrastructure.multi_message_service import MultiMessageService
from wulifang.infrastructure.tray_message_service import TrayMessageService

import nuke


def _reload():
    import wulifang.nuke

    wulifang.nuke.reload()


def init_gui():
    nuke.menu("Nuke".encode("utf-8")).addMenu("帮助".encode("utf-8")).addCommand(
        "重新加载吾立方插件".encode("utf-8"),
        _reload,
        "Ctrl+Shift+F5".encode("utf-8"),
    )
    wulifang.message = MultiMessageService(wulifang.message, TrayMessageService())
