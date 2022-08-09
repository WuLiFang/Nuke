# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals


import hiero.core
import sys

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def install(p):
    # type: (Text) -> None
    sys.path.insert(0, p)
    hiero.core.addPluginPath(p)
