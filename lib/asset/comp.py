# -*- coding=UTF-8 -*-
"""Comp script file.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wlf.fileutil import copy


def sent_to_dir(dir_):
    """Send current working file to dir."""

    _ = copy(nuke.value(b"root.name"), dir_, threading=True)
