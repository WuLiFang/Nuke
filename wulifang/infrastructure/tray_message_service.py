# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false
"""send notification messsages to user.  """

from __future__ import absolute_import, division, print_function, unicode_literals

from wulifang.vendor.Qt.QtGui import QIcon
from wulifang.vendor.Qt.QtWidgets import QSystemTrayIcon

from .. import pathtools

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text
    from ..types import MessageService


class TrayMessageService:
    def __init__(self):
        self._icon = QSystemTrayIcon()
        self._icon.setIcon(QIcon(pathtools.workspace("assets", "tray_icon.png")))

    def info(self, message, title=""):
        # type: (Text, Text) -> None
        self._icon.show()
        self._icon.showMessage(
            title, message, icon=QSystemTrayIcon.Information, msecs=3000
        )

    def error(self, message, title=""):
        # type: (Text, Text) -> None
        self._icon.show()
        self._icon.showMessage(
            title, message, icon=QSystemTrayIcon.Critical, msecs=3000
        )

    def debug(self, message, title=""):
        # type: (Text, Text) -> None
        pass


def _(v):
    # type: (TrayMessageService) -> MessageService
    return v
