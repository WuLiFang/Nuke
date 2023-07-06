# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Optional
    from wulifang.vendor.Qt import QtWidgets


def main_window():
    # type: () -> Optional[QtWidgets.QMainWindow]

    from wulifang.vendor.Qt import QtWidgets

    for i in QtWidgets.QApplication.topLevelWidgets():
        if isinstance(i, QtWidgets.QMainWindow):
            return i
