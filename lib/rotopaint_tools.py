# -*- coding=UTF-8 -*-
"""Rotopaint scripting tools.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke.rotopaint

LIFETIME_TYPE_ALL = 0
LIFETIME_TYPE_START_TO_FRAME = 1
LIFETIME_TYPE_SINGLE_FRAME = 2
LIFETIME_TYPE_FRAME_TO_END = 3
LIFETIME_TYPE_RANGE = 4


def iter_layer(layer):
    """Iterate layer items from rotopaint layer recursively.

    Args:
        layer (nuke.rotopaint.Layer): the layer to iterate.

    Yields:
        nuke.rotopaint.Element: Element in this layer
    """
    # type: (nuke.rotopaint.Layer,) -> Iterator[nuke.rotopaint.Element]
    for i in layer:
        yield i
        if isinstance(i, nuke.rotopaint.Layer):
            for j in _iter_layer(i):
                yield j
