# -*- coding: UTF-8 -*-
"""Nuke init file.  """
from __future__ import absolute_import, print_function, unicode_literals


def _wlf_plugin_setup():
    """Main entry.  """

    import logging
    import os
    import re
    import sys

    from lib import __version__
    from wlf.files import map_drivers
    from wlf.mp_logging import set_basic_logger
    from wlf.path import get_encoded
    import callback

    set_basic_logger(logging.getLogger('com.wlf'))

    # Validation.
    try:
        import validation
    except ImportError:
        __import__('nuke').message('Plugin\n {} crushed.'.format(
            os.path.normpath(os.path.join(__file__, '../../'))))
        sys.exit(1)

    print('-' * 20)
    print(get_encoded('吾立方插件 {}\n许可至: {}'.format(__version__,
                                                 validation.EXPIRE_AT)))
    print('-' * 20)
    del validation.EXPIRE_AT

    # Map drivers.
    if sys.platform == 'win32':
        if re.match(r'(?i)wlf(\d+|\b)', os.getenv('ComputerName')):
            map_drivers()

    callback.init()


if __name__ == '__main__':
    _wlf_plugin_setup()
