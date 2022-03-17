# -*- coding=UTF-8 -*-
# pyright: strict
"""message to user.  """

from __future__ import absolute_import, division, print_function, unicode_literals


import hiero.ui
from wulifang.vendor.Qt import QtWidgets

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def info(text, title=""):
    # type: (Text, Text) -> None
    QtWidgets.QMessageBox.information(hiero.ui.mainWindow().parentWidget(), title, text)


def error(text, title=""):
    # type: (Text, Text) -> None
    QtWidgets.QMessageBox.critical(hiero.ui.mainWindow().parentWidget(), title, text)

