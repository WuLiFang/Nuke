# -*- coding: UTF-8 -*-
"""Nuke init file.  """
import os
import sys
import re
import nuke

from wlf import files
import callback

print("python sys.setdefaultencoding('UTF-8')")
reload(sys)
sys.setdefaultencoding('UTF-8')

print(u'吾立方插件初始化')

if re.match(r'(?i)wlf(\d+|\b)', os.getenv('ComputerName')):
    print(u'映射网络驱动器')
    files.map_drivers()
print(u'添加插件节点')
nuke.pluginAddPath('plugins')
print(u'添加init callback')
callback.init()
