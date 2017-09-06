# -*- coding: UTF-8 -*-
"""Nuke init file.  """
import os
import sys
import re


from wlf import files
import callback

try:
    __import__('validation')
except ImportError:
    __import__('nuke').message('Plugin\n {} crushed.'.format(
        os.path.normpath(os.path.join(__file__, '../../'))))
    sys.exit(1)

print("python sys.setdefaultencoding('UTF-8')")
reload(sys)
sys.setdefaultencoding('UTF-8')

print(u'吾立方插件初始化')

if re.match(r'(?i)wlf(\d+|\b)', os.getenv('ComputerName')):
    print(u'映射网络驱动器')
    files.map_drivers()
print(u'添加init callback')
callback.init()
