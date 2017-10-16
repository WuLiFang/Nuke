"""Wrap QWidget to nuke panel.  """

import nuke
from nukescripts.panels import PythonPanel, registerPanel

__version__ = '0.1.1'


def register(widget, name, widget_id, create=False):
    """registerWidgetAsPanel(widget, name, id, create) -> PythonPanel

      Wraps and registers a widget to be used in a Nuke panel.

      widget - should be a string of the class for the widget
      name - is is the name as it will appear on the Pane menu
      widget_id - should the the unique ID for this widget panel
      create - if this is set to true a new NukePanel will be returned that wraps this widget
    """

    class _Panel(PythonPanel):

        def __init__(self, widget, name, widget_id):
            PythonPanel.__init__(self, name, widget_id)
            self.custom_knob = nuke.PyCustom_Knob(
                name, "",
                "__import__('nukescripts').panels.WidgetKnob("
                "__import__('{0.__module__}', globals(), locals(), ['{0.__name__}'])"
                ".{0.__name__})".format(widget))
            self.addKnob(self.custom_knob)

    def _add():
        return _Panel(widget, name, widget_id).addToPane()

    menu = nuke.menu('Pane')
    menu.addCommand(name, _add)
    registerPanel(widget_id, _add)

    if (create):
        return _Panel(widget, name, widget_id)
