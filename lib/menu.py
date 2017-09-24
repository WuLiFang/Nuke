# -*- coding: UTF-8 -*-
"""Nuke menu file."""
import _ui
import callback
import pref
from wlf import cgtwq

_ui.add_menu()
_ui.add_panel()
_ui.add_autolabel()
pref.add_preferences()
pref.set_knob_default()
callback.menu()

if cgtwq.MODULE_ENABLE:
    cgtwq.CGTeamWork.update_status()
