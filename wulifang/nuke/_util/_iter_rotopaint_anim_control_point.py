# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke.rotopaint
import nuke.curvelib

from ._relative_rotopaint_anim_control_point import RelativeRotopaintAnimControlPoint

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterator, Union


def iter_rotopaint_anim_control_point(point):
    # type: (nuke.rotopaint.ShapeControlPoint) -> Iterator[Union[nuke.curvelib.AnimControlPoint, RelativeRotopaintAnimControlPoint]]
    """Iterate AnimControlPoint in given shape point,
    Relative point is wrapped with RelativePointProxy
    so we can treat all points as absolute.

    Args:
        point (nuke.rotopaint.ShapeControlPoint): The point to iterate.

    Yields:
        Iterator[Union[nuke.rotopaint.AnimControlPoint, RelativePointProxy]]:
            items in point.
    """

    yield point.center
    yield RelativeRotopaintAnimControlPoint(point.leftTangent, point.center)
    yield RelativeRotopaintAnimControlPoint(point.rightTangent, point.center)
    yield RelativeRotopaintAnimControlPoint(point.featherCenter, point.center)
    yield RelativeRotopaintAnimControlPoint(point.featherLeftTangent, point.center)
    yield RelativeRotopaintAnimControlPoint(point.featherRightTangent, point.center)
