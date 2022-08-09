# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals
import os

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


_DIR = os.path.dirname(os.path.abspath(__file__))
_WORKSPACE = os.path.dirname(_DIR)


def workspace(*paths):
    # type: (Text) -> Text
    return os.path.join(_WORKSPACE, *paths)
