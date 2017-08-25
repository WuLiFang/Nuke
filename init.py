# -*- coding: UTF-8 -*-
"""Nuke init file.  """
import os
import sys

import nuke

sys.path.append(os.path.join(__file__, '../lib'))
nuke.pluginAddPath('plugins')
