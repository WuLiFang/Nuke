# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


from wulifang._util import assert_isinstance, cast_str

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def raise_panel(name):
    # type: (Text,) -> None
    """raise panel by name.

    Args:
        name (str): panel name, (e.g. DopeSheet.1)

    Raises:
        RuntimeError: when panel not found.
    """

    from wulifang.vendor.Qt import QtWidgets

    for i in QtWidgets.QApplication.topLevelWidgets():
        panel = i.findChild(QtWidgets.QWidget, cast_str(name))
        if not panel:
            continue

        parent = panel.parentWidget()
        if not isinstance(parent, QtWidgets.QStackedWidget):
            continue
        parent = assert_isinstance(parent, QtWidgets.QStackedWidget)
        index = parent.indexOf(panel)
        parent = parent.parentWidget()
        if not isinstance(parent, QtWidgets.QWidget):
            continue
        tab = parent.findChild(QtWidgets.QTabBar)
        if not tab:
            continue
        tab.setCurrentIndex(index)
        panel.window().raise_()
        return
    else:
        raise RuntimeError("no such panel: %s" % (name,))
