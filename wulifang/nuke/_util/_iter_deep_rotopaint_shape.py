# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke.rotopaint
from ._iter_deep_rotopaint_element import iter_deep_rotopaint_element

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterator


def iter_deep_rotopaint_shape(layer):
    # type: (nuke.rotopaint.Layer) -> Iterator[nuke.rotopaint.Shape]
    for i in iter_deep_rotopaint_element(layer):
        if isinstance(i, nuke.rotopaint.Shape):
            yield i
