# -*- coding=UTF-8 -*-
"""Windows ignore file.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# pylint: disable=missing-docstring
import os
import re

import nuke

from wlf.codectools import is_ascii

from ..core import HOOKIMPL


@HOOKIMPL
def is_ignore_filename(filename):
    ignore_pat = (r'thumbs\.db$', r'.*\.lock$', r'.* - 副本\b')
    basename = os.path.basename(filename)
    for pat in ignore_pat:
        if re.match(pat, basename, flags=re.I | re.U):
            return True
    if filename.lower().endswith('.mov') and not is_ascii(filename):
        nuke.createNode(
            'StickyNote',
            'autolabel {{\'<div align="center">\'+autolabel()+\'</div>\'}} '
            'label {{{}\n\n'
            '<span style="color:red;text-align:center;font-weight:bold">'
            'mov格式使用非英文路径将可能导致崩溃</span>}}'.format(filename).encode('utf-8'),
            inpanel=False)
        return True
    return None
