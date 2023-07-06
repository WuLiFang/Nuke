# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    import _rotopaint

    RotoKnob = _rotopaint.RotoKnob
else:
    try:
        import _rotopaint

        RotoKnob = _rotopaint.RotoKnob
    except:
        import nuke.curveknob

        class RotoKnob(nuke.curveknob.CurveKnob):
            def __init__(self, *_args, **_kwargs):
                raise RuntimeError("RotoKnob not available")
