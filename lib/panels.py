# -*- coding=UTF-8 -*-
"""Wrap QWidget to nuke panel.  """

from __future__ import absolute_import, unicode_literals

import nuke
import nukescripts  # pylint: disable=import-error

import cast_unknown as cast


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import AnyStr, Any


class PythonPanel(nukescripts.PythonPanel):
    """Customized python panel.  """

    is_dialog = False
    pane_name = None

    def __getitem__(self, name):
        # type: (AnyStr,) -> nuke.Knob
        return self.knobs()[cast.binary(name)]

    def show(self):
        """Show panel.  """
        pane = nuke.getPaneFor(b'Properties.1')
        if pane:
            self.addToPane(pane)
        else:
            self.is_dialog = True
            super(PythonPanel, self).show()

    def destroy(self):
        """Destroy panel.  """

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
                name_e, b"",
                ("__import__('nukescripts').panels.WidgetKnob("
                 "__import__('{0.__module__}', globals(), locals(), ['{0.__name__}'])"
                 ".{0.__name__})").format(widget))
            self.addKnob(self.custom_knob)

    def _add():
        return _Panel(widget, name, widget_id).addToPane()

    menu = nuke.menu(b'Pane')
    _ = menu.addCommand(cast.binary(name), _add)
    nukescripts.registerPanel(widget_id, _add)

    if create:
        return _Panel(widget, name, widget_id)
