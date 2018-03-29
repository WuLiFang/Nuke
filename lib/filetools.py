# -*- coding=UTF-8 -*-
"""Tools for file operations.   """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

from wlf.path import PurePath

ROOT = os.path.abspath(os.path.dirname(__file__))


def path(*other):
    """Get path relative to `ROOT`.

    Returns:
        PurePath -- Absolute path under root.
    """

    ret = PurePath(ROOT)
    for i in other:
        ret /= i
    return ret
