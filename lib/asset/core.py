# -*- coding: UTF-8 -*-
"""Deal with assets and files in nuke."""


from __future__ import absolute_import, division, print_function, unicode_literals

from wlf.pathtools import make_path_finder

module_path = make_path_finder(__file__)  # pylint: disable=invalid-name
TEMPLATES_DIR = module_path("../templates")

CACHED_ASSET = set()

# Asset type
A_SEQUENCE = 1 << 0
A_SINGLEFILE = 1 << 1
