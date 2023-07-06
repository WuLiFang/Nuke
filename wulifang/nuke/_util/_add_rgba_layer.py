# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke
from wulifang._util import cast_str

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def add_rgba_layer(
    name,  # type: Text
):
    if cast_str(name) in nuke.layers():
        return
    return nuke.Layer(
        cast_str(name),
        [
            cast_str("{}.{}".format(name, channel))
            for channel in ("red", "green", "blue", "alpha")
        ],
    )
