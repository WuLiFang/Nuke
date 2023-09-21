# -*- coding=UTF-8 -*-
# pyright: ignore, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


from ._clamp import clamp

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, TypeVar, Sequence

    T = TypeVar("T")


def hex_color(color):
    # type: (Sequence[float]) -> Text
    if len(color) == 1:
        return hex_color((color[0], color[0], color[0]))
    if len(color) == 3:
        return "#%02X%02X%02X" % (
        clamp(0, 255, round(color[0] * 255)),
        clamp(0, 255, round(color[1] * 255)),
        clamp(0, 255, round(color[2] * 255)),
    )
    if len(color) == 4:
        return "#%02X%02X%02X%02X" % (
        clamp(0, 255, round(color[0] * 255)),
        clamp(0, 255, round(color[1] * 255)),
        clamp(0, 255, round(color[2] * 255)),
        clamp(0, 255, round(color[3] * 255)),
    )

    raise ValueError("invalid color", color)
