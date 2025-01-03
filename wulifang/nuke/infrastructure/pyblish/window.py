# -*- # -*- coding=UTF-8 -*-
"""Pyblish lite nuke interagation.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import codecs


import wulifang
import wulifang.nuke
from wulifang.vendor.pyblish_lite import control, delegate, settings, util, window
from wulifang.vendor.Qt import QtGui
from wulifang.vendor.Qt.QtCore import Qt
from wulifang.vendor.Qt.QtWidgets import QApplication
from wulifang._util import workspace_path, cast_str
from wulifang.nuke._util import main_window, raise_panel

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Optional, Text

def _on_processed(result):
    def _get_text():
        records = result["records"]
        if records:
            return "\n".join(i.getMessage() for i in records)

        return "请在发布窗口的最后一个标签中查看详情"

    if not result["success"]:
        wulifang.message.info(_get_text(), title="发布失败")


class Window(window.Window):
    """Modified pyblish_lite window for nuke.

    Args:
        parent (QtCore.QObject): Qt parent.

    Raises:
        ValueError: When already exists another pyblish window.
    """

    last_instance = None

    def __init__(self):

        controller = control.Controller()
        parent = main_window() or QApplication.activeWindow()
        controller.was_processed.connect(_on_processed)
        self.controller = controller  # type hint
        super(Window, self).__init__(controller, parent)

        self.resize(*settings.WindowSize)
        self.setWindowTitle(settings.WindowTitle)

        with codecs.open(
            workspace_path("assets", "pyblish_lite.css"), encoding="utf-8"
        ) as f:
            css = f.read()

        # Make relative paths absolute
        root = util.get_asset("").replace("\\", "/")
        css = css.replace('url("', 'url("%s' % root)
        self.setStyleSheet(cast_str(css))

        self.setObjectName("PyblishWindow")
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        Window.last_instance = self

        def _cleanup():
            self.close()

        wulifang.cleanup.add(_cleanup)

    def activate(self):
        """Active pyblish window."""

        if self.isWindow():
            self.showNormal()
        else:
            raise_panel("com.wlf.pyblish")

    def get_parent(self, parent_class):
        """Get parent for window.

        Args:
            parent_class (class): Parent class

        Raises:
            ValueError: No such parent.

        Returns:
            parent_class: First matched parent.
        """

        parent = self
        while parent:
            parent = parent.parent()
            if isinstance(parent, parent_class):
                return parent
        raise ValueError("No such parent")


# XXX: will be called by nuke.PanelNode.createWidget
setattr(Window, "updateValue", lambda *args, **kwargs: None)


def set_preferred_fonts(font, scale_factor=None):
    # type: (Text, Optional[float]) -> None
    """Set preferred font."""

    if scale_factor:
        delegate.scale_factor = scale_factor
    else:
        scale_factor = delegate.scale_factor
    delegate.fonts.update(
        {
            "h3": QtGui.QFont(font, 10 * scale_factor, 900),
            "h4": QtGui.QFont(font, 8 * scale_factor, 400),
            "h5": QtGui.QFont(font, 8 * scale_factor, 800),
        }
    )
