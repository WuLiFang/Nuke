# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Type

import sys

PY2 = sys.version_info[0] == 2


def _text_type():
    # type: () -> Type[str]
    if PY2:
        return unicode  # type: ignore
    return str


text_type = _text_type()


def _binary_type():
    # type: () -> Type[bytes]
    if PY2:
        return str  # type: ignore
    return bytes


binary_type = _binary_type()
