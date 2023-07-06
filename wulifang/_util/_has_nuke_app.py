# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import sys


def has_nuke_app():
    """Return if in nuke environment."""

    return bool(sys.modules.get("nuke"))
