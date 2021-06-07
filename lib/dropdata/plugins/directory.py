# -*- coding=UTF-8 -*-
"""Directory dropdata handle.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import os

import nuke

import cast_unknown as cast

from ..core import HOOKIMPL

# pylint: disable=missing-docstring


@HOOKIMPL
def get_filenames(url):
    ret = []
    if not os.path.isdir(cast.binary(url)):
        return ret
    for dirpath, _, _ in os.walk(cast.binary(url)):
        dirpath = cast.text(dirpath).replace("\\", "/")
        filenames = nuke.getFileNameList(cast.binary(dirpath))
        filenames = ["{}/{}".format(dirpath, cast.text(i)) for i in filenames]
        ret.extend(filenames)
    return ret
