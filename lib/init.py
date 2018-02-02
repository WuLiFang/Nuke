# -*- coding: UTF-8 -*-
"""Nuke init file.  """
from __future__ import absolute_import, print_function, unicode_literals

_GLOBAL_BEFORE_INIT = dict(globals())


def main():
    import logging
    import os
    import re
    import sys

    from lib import __version__
    from wlf.files import map_drivers
    from wlf.mp_logging import set_basic_logger
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
    print('吾立方插件 {}\n许可至: {}'.format(__version__,
                                     validation.EXPIRE_AT).encode(sys.stdout.encoding or 'utf8'))
    print('-' * 20)
    del validation.EXPIRE_AT

    # Map drivers.
    if sys.platform == 'win32':
        if re.match(r'(?i)wlf(\d+|\b)', os.getenv('ComputerName')):
            map_drivers()

    callback.init()

    # Recover outter scope env.
    globals().update(_GLOBAL_BEFORE_INIT)


if __name__ == '__main__':
    main()
