# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke
import nuke.rotopaint
import _rotopaint

from wulifang._util import (
    assert_isinstance,
    cast_str,
)


def rotopaint_root_layer(node):
    # type: (nuke.Node) -> nuke.rotopaint.Layer

    return assert_isinstance(
        node[cast_str("curves")],
        _rotopaint.RotoKnob,
    ).rootLayer
