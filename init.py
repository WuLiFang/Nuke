# -*- coding: UTF-8 -*-
"""Nuke init file.  """
import nuke

import six
print("six path: %s" % six.__file__)

nuke.pluginAddPath(b'lib')
nuke.pluginAddPath(b'plugins')

