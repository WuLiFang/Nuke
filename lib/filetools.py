# -*- coding=UTF-8 -*-
"""Tools for file operations.   """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

from wlf.path import PurePath
from wlf.pathtools import make_path_finder

ROOT = os.path.abspath(os.path.dirname(__file__))
module_path = make_path_finder(__file__)  # pylint: disable = invalid-name
plugin_folder_path = make_path_finder(  # pylint: disable = invalid-name
    module_path())


def path(*other):
    """Get path relative to `ROOT`.

    Returns:
        PurePath -- Absolute path under root.
    """

    ret = PurePath(ROOT)
    for i in other:
        ret /= i
    return ret
