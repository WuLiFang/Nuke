# -*- coding=UTF-8 -*-
# pyright: strict
""".  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

if True:
    import os
    import sys
    WORKSPACE_FOLDER =  os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(0, WORKSPACE_FOLDER)

import wulifang.hiero

wulifang.hiero.init()
