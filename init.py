# -*- coding: UTF-8 -*-
"""Nuke init file."""
import os
import sys
import nuke

print("python sys.setdefaultencoding('UTF-8')")
reload(sys)
sys.setdefaultencoding('UTF-8')

print(u'吾立方插件初始化')
try:
    sys.path.append(os.path.join(__file__, '../py'))
    from wlf import callback, pref, files
except ImportError:
    raise

print(u'映射网络驱动器')
files.map_drivers()
print(u'添加插件节点')
nuke.pluginAddPath('plugins')
print(u'添加init callback')
callback.init()
