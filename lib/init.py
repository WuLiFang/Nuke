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


def setup_prefix_filter():
    """Add custom prefix filter for wrong naming.  """

    import cgtwq.helper.wlf
    cgtwq.helper.wlf.CGTWQHelper.prefix_filters.append(
        lambda x: x.replace('XJCG', 'XJ'))


setup_site()
setup_prefix_filter()


def main():
    import os
    import sys
    import callback
    import render
    import wlf.mp_logging

    try:
        import validation
    except ImportError:
        __import__('nuke').message('Plugin\n {} crushed.'.format(
            os.path.normpath(os.path.join(__file__, '../../'))))
        sys.exit(1)

    wlf.mp_logging.basic_config()

    validation.setup()
    callback.setup()
    render.setup()

    # Recover outter scope env.
    globals().update(_GLOBAL_BEFORE_INIT)


if __name__ == '__main__':
    main()
