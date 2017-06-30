# -*- coding: UTF-8 -*-
import nuke

import wlf

nuke.pluginAddPath('plugins\icons')

wlf.ui.add_menu()
wlf.callback.menu()
wlf.callback.add_dropdata_callback()
wlf.pref.add_preferences()
