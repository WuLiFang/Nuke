# -*- coding: UTF-8 -*-
import nuke

import wlf

nuke.pluginAddPath('plugins\icons')

wlf.ui.add_menu()
wlf.callback.menu()
wlf.pref.add_preferences()
