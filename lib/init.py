# -*- coding: UTF-8 -*-
"""Nuke init file.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

_GLOBAL_BEFORE_INIT = dict(globals())


def setup_site():
    """Add local site-packages to python.  """
    import site
    import os

    site.addsitedir(os.path.abspath(
        os.path.join(__file__, '../site-packages')))


setup_site()


def _enable_windows_unicode_console():
    import sys
    if sys.platform != 'win32':
        return
    import win_unicode_console
    win_unicode_console.enable()


def main():
    _enable_windows_unicode_console()

    import os
    import sys
    import callback
    import render
    import wlf.mp_logging
    import patch.precomp
    import logging

    try:
        import validation
    except ImportError:
        __import__('nuke').message('Plugin\n {} crushed.'.format(
            os.path.normpath(os.path.join(__file__, '../../'))))
        sys.exit(1)

    wlf.mp_logging.basic_config()
    pyblish_logger = logging.getLogger("pyblish")
    if pyblish_logger.getEffectiveLevel() > logging.DEBUG:
        pyblish_logger.setLevel(logging.CRITICAL)

    validation.setup()
    callback.setup()
    render.setup()
    patch.precomp.enable()

    # Recover outter scope env.
    globals().update(_GLOBAL_BEFORE_INIT)


if __name__ == '__main__':
    main()
