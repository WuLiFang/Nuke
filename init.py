# -*- coding: UTF-8 -*-
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'py'))
import wlf

nuke.pluginAddPath('plugins')
wlf.callback.init()
wlf.pref.set_knob_default()
os.environ['NUKE_FONT_PATH'] = '//SERVER/scripts/NukePlugins/Fonts'
