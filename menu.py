# -*- coding: UTF-8 -*-
import nuke

from wlf import ui, callback, pref, cgtwn

nuke.pluginAddPath('plugins/icons')

ui.add_menu()
callback.menu()
pref.add_preferences()
cgtwn.CGTeamWork.update_status()
