# -*- coding: UTF-8 -*-
import nuke

from wlf import ui, callback, pref

nuke.pluginAddPath('plugins/icons')

ui.add_menu()
callback.menu()
pref.add_preferences()
