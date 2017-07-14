# -*- coding: UTF-8 -*-
"""Nuke init file."""

import nuke

try:
    from wlf import callback, pref
except ImportError as ex:
    import os
    import sys
    sys.path.append(os.path.join(__file__, '../py'))
    from wlf import callback, pref

nuke.pluginAddPath('plugins')
callback.init()
pref.set_knob_default()
