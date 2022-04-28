# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import wulifang
from wulifang.infrastructure.multi_message_service import MultiMessageService
from wulifang.infrastructure.tray_message_service import TrayMessageService

import nuke

_LOGGER = logging.getLogger(__name__)


def _reload():
    from ._init import reload

    _LOGGER.info("reload")
    reload()


def init_gui():
    nuke.menu("Nuke".encode("utf-8")).addMenu("帮助".encode("utf-8")).addCommand(
        "重新加载吾立方插件".encode("utf-8"),
        _reload,
        "Ctrl+Shift+F5".encode("utf-8"),
    )
    wulifang.message = MultiMessageService(wulifang.message, TrayMessageService())
