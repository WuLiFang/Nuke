# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


def has_qt_app():
    try:
        from wulifang.vendor.Qt.QtWidgets import QApplication

        return bool(QApplication.instance())
    except ImportError:
        return False
