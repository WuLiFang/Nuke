# -*- coding: UTF-8 -*-
"""Nuke init file.  """

from __future__ import print_function, unicode_literals, absolute_import

import os
import sys
import re
import logging

from wlf.files import map_drivers
from wlf.mp_logging import set_basic_logger
from wlf.env import set_default_encoding


__version__ = '0.4.19'

LOGGER = logging.getLogger('com.wlf')


def main():
    """Main entry.  """

    import callback

    set_basic_logger(LOGGER)
    set_default_encoding('UTF-8')

    # Validation.
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

    # Map drivers.
    if sys.platform == 'win32':
        if re.match(r'(?i)wlf(\d+|\b)', os.getenv('ComputerName')):
            map_drivers()

    callback.init()


if __name__ == '__main__':
    main()
