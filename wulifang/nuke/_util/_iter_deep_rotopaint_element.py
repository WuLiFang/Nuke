# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke.rotopaint

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterator


def iter_deep_rotopaint_element(layer):
    # type: (nuke.rotopaint.Layer) -> Iterator[nuke.rotopaint.Element]
    for i in layer:
        yield i
        if isinstance(i, nuke.rotopaint.Layer):
            for j in iter_deep_rotopaint_element(i):
                yield j
