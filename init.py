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
    from wlf import callback, pref
except ImportError:
    raise

print(u'添加插件节点')
nuke.pluginAddPath('plugins')
print(u'添加init callback')
callback.init()
print(u'设置knob默认值')
pref.set_knob_default()
