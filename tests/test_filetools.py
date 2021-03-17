# -*- coding=UTF-8 -*-
"""Test `filetools` module.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

import filetools
import cast_unknown as cast


def test_plugin_folder_path():
    path = filetools.plugin_folder_path('ToolSets')
    assert os.path.exists(cast.binary(path)), path
