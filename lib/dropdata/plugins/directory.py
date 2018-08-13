# -*- coding=UTF-8 -*-
"""Directory dropdata handle.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

import nuke

from wlf.codectools import get_encoded as e
from wlf.codectools import get_unicode as u

from ..core import HOOKIMPL

# pylint: disable=missing-docstring


@HOOKIMPL
def get_filenames(url):
    ret = []
    if not os.path.isdir(e(url)):
        return ret
    for dirpath, _, _ in os.walk(e(url)):
        dirpath = u(dirpath.replace('\\', '/'))
        filenames = nuke.getFileNameList(e(dirpath, 'UTF-8'))
        filenames = ['{}/{}'.format(dirpath, u(i)) for i in filenames]
        ret.extend(filenames)
    return ret
