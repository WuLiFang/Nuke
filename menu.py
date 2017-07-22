# -*- coding: UTF-8 -*-
import nuke

from wlf import ui, callback, pref, asset

nuke.pluginAddPath('plugins/icons')

ui.add_menu()
callback.menu()
pref.add_preferences()
# asset.DropFrameCheck().start()
