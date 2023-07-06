# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false
"""send notification messsages to user.  """

from __future__ import absolute_import, division, print_function, unicode_literals

from wulifang.vendor.Qt.QtGui import QIcon
from wulifang.vendor.Qt.QtWidgets import QSystemTrayIcon


from wulifang._util import workspace_path

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text
    from .._types import MessageService


class TrayMessageService:
    def __init__(self):
        self._icon = QSystemTrayIcon()
        self._icon.setIcon(QIcon(workspace_path("assets", "icons", "wulifang.png")))

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
