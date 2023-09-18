# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke


def process_events():
    if not nuke.GUI:
        return
    from wulifang.vendor.Qt.QtCore import QCoreApplication

    QCoreApplication.processEvents()
