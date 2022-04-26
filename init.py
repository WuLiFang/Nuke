# -*- coding: UTF-8 -*-
"""Nuke init file.  """
import nuke
import wulifang.nuke

nuke.pluginAddPath(b"lib")
nuke.pluginAddPath(b"plugins")
wulifang.nuke.init()
