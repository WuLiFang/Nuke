# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke
import nukescripts

from wulifang._util import cast_str
import wulifang

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text

    PythonPanel = nukescripts.PythonPanel
else:
    if nuke.GUI:
        PythonPanel = nukescripts.PythonPanel
    else:
        class PythonPanel(object):
            def __init__(self, *args, **kwargs):
                raise RuntimeError("PythonPanel not available")
        


class Panel(PythonPanel):
    """Customized python panel."""

    is_dialog = False
    pane_name = None

    @staticmethod
    def register(
        id,  # type: Text
        name,  # type: Text
        widget,  # type: Panel
        create=False,  # type: bool
    ):
        # type: (...) -> ...

        class PanelWrapper(Panel):
            def __init__(
                self,
                widget,  # type: Panel
                name,  # type: Text
                id,  # type: Text
            ):
                name_str = cast_str(name)
                super(PanelWrapper, self).__init__(name_str, cast_str(id))
                self.custom_knob = nuke.PyCustom_Knob(
                    name_str,
                    cast_str(""),
                    cast_str(
                        (
                            "__import__('nukescripts').panels.WidgetKnob("
                            "__import__('{0.__module__}', globals(), locals(), ['{0.__name__}'])"
                            ".{0.__name__})"
                        ).format(widget)
                    ),
                )
                self.addKnob(self.custom_knob)

                def dispose():
                    self.destroy()

                wulifang.cleanup.add(dispose)

        def add_to_pane():
            return PanelWrapper(widget, name, id).addToPane()

        menu = nuke.menu(cast_str("Pane"))
        menu.addCommand(cast_str(name), add_to_pane)
        nukescripts.registerPanel(cast_str(id), add_to_pane)

        def dispose():
            nukescripts.unregisterPanel(cast_str(id), add_to_pane)

        wulifang.cleanup.add(dispose)
        if create:
            return PanelWrapper(widget, name, id)

    @staticmethod
    def restore(id):
        # type: (Text) -> None
        nukescripts.panels.restorePanel(cast_str(id))

    def __getitem__(self, name):
        # type: (Text,) -> nuke.Knob
        return self.knobs()[cast_str(name)]

    def show(self):
        """Show panel."""
        pane = nuke.getPaneFor(cast_str("Properties.1"))
        if pane:
            self.addToPane(pane)
        else:
            self.is_dialog = True
            super(Panel, self).show()

    def destroy(self):
        """Destroy panel."""

        self.removeCallback()
        if self.is_dialog:
            nuke.thisPane().destroy()
        nukescripts.PythonPanel.destroy(self)  # type: ignore
