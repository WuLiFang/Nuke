# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke
import wulifang.nuke
from wulifang._util import (
    workspace_path,
    cast_str,
)

nuke.pluginAddPath(cast_str(workspace_path("plugins")))
# TODO: fully support nuke13
if nuke.NUKE_VERSION_MAJOR <= 12:
    nuke.pluginAddPath(cast_str(workspace_path("lib")))
wulifang.nuke.init()
