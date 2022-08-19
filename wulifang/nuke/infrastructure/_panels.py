# -*- coding=UTF-8 -*-
"""nuke panels.  """

from __future__ import absolute_import, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import AnyStr, Any

import nuke
import nukescripts
import wulifang.vendor.cast_unknown as cast
from wulifang.vendor.Qt import QtWidgets


class PythonPanel(nukescripts.PythonPanel):
    """Customized python panel."""

    is_dialog = False
    pane_name = None

    def __getitem__(self, name):
        # type: (AnyStr,) -> nuke.Knob
        return self.knobs()[cast.binary(name)]

    def show(self):
        """Show panel."""
        pane = nuke.getPaneFor(b"Properties.1")
        if pane:
            self.addToPane(pane)
        else:
            self.is_dialog = True
            super(PythonPanel, self).show()

    def destroy(self):
        """Destroy panel."""

        self.removeCallback()
        if self.is_dialog:
            nuke.thisPane().destroy()
        super(PythonPanel, self).destroy()


def register(widget, name, widget_id, create=False):
    # type: (bytes, bytes, bytes, bool) -> Any
    """registerWidgetAsPanel(widget, name, id, create) -> PythonPanel

    Wraps and registers a widget to be used in a Nuke panel.

    widget - should be a string of the class for the widget
    name - is is the name as it will appear on the Pane menu
    widget_id - should the the unique ID for this widget panel
    create - if this is set to true a new NukePanel will be returned that wraps this widget
    """

    class _Panel(PythonPanel):
        def __init__(self, widget, name, widget_id):
            name_e = cast.binary(name)
            super(_Panel, self).__init__(name_e, widget_id)
            self.custom_knob = nuke.PyCustom_Knob(
                name_e,
                b"",
                (
                    "__import__('nukescripts').panels.WidgetKnob("
                    "__import__('{0.__module__}', globals(), locals(), ['{0.__name__}'])"
                    ".{0.__name__})"
                ).format(widget),
            )
            self.addKnob(self.custom_knob)

    def _add():
        return _Panel(widget, name, widget_id).addToPane()

    menu = nuke.menu(b"Pane")
    _ = menu.addCommand(cast.binary(name), _add)
    nukescripts.registerPanel(widget_id, _add)

    if create:
        return _Panel(widget, name, widget_id)


def main_window():
    """Get nuke mainwindow.

    Returns:
        Optional[QtWidgets.QMainWindow]: Nuke main window.
    """

    for i in QtWidgets.QApplication.topLevelWidgets():
        if isinstance(i, QtWidgets.QMainWindow):
            return i


def raise_(name):
    # type: (str,) -> None
    """raise panel by name.

    Args:
        name (str): panel name, (e.g. DopeSheet.1)

    Raises:
        RuntimeError: when panel not found.
    """

    for i in QtWidgets.QApplication.topLevelWidgets():
        panel = i.findChild(QtWidgets.QWidget, name)
        if not panel:
            continue

        parent = panel.parentWidget()
        if not isinstance(parent, QtWidgets.QStackedWidget):
            continue
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
        raise RuntimeError("Not found panel: {}".format(name))
