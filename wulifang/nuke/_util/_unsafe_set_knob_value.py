# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def unsafe_set_knob_value(knob, value, channel=""):
    # type: (nuke.Knob, object, Text) -> None
    if channel:
        knob.setValue(value, channel)  # type: ignore
    else:
        knob.setValue(value)  # type: ignore
