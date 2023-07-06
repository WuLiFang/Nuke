# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke


def copy_knob_flags(
    dst,  # type: nuke.Knob
    src,  # type: nuke.Knob
):
    # type: (...) -> ...
    # Set all possible flag.
    for flag in (pow(2, n) for n in range(31)):
        if src.getFlag(flag):
            dst.setFlag(flag)
        else:
            dst.clearFlag(flag)
