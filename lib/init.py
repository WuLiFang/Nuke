# -*- coding: UTF-8 -*-
"""Nuke init file.  """
import os
import sys
import re
import logging

from wlf import files
from wlf.mp_logging import set_basic_logger
import callback

__version__ = '0.4.16'

LOGGER = logging.getLogger('com.wlf')
set_basic_logger(LOGGER)

if sys.getdefaultencoding != 'UTF-8':
    reload(sys)
    LOGGER.debug("python sys.setdefaultencoding('UTF-8')")
    sys.setdefaultencoding('UTF-8')

try:
    import validation
except ImportError:
    __import__('nuke').message('Plugin\n {} crushed.'.format(
        os.path.normpath(os.path.join(__file__, '../../'))))
    sys.exit(1)

print('-' * 20)
print(u'吾立方插件 {}\n许可至: {}'.format(__version__, validation.EXPIRE_AT))
print('-' * 20)
del validation.EXPIRE_AT

if sys.platform == 'win32':
    if re.match(r'(?i)wlf(\d+|\b)', os.getenv('ComputerName')):
        LOGGER.info(u'映射网络驱动器')
        files.map_drivers()

callback.init()
