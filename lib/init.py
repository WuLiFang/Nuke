# -*- coding: UTF-8 -*-
"""Nuke init file.  """

from __future__ import absolute_import, division, print_function, unicode_literals

_GLOBAL_BEFORE_INIT = dict(globals())


def setup_site():
    """Add local site-packages to python."""
    import site
    import os

    site.addsitedir(os.path.abspath(os.path.join(__file__, "../site-packages")))


def main():
    setup_site()

    # Recover outer scope env.
    globals().update(_GLOBAL_BEFORE_INIT)


if __name__ == "__main__":
    main()
