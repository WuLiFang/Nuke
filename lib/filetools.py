# -*- coding=UTF-8 -*-
"""Tools for file operations.   """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from wlf.pathtools import make_path_finder

module_path = make_path_finder(__file__)  # pylint: disable = invalid-name
plugin_folder_path = make_path_finder(  # pylint: disable = invalid-name
    module_path())
