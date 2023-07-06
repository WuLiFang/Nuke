# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke.curvelib


class RelativeRotopaintAnimControlPoint:
    def __init__(self, point, center):
        # type: (nuke.curvelib.AnimControlPoint, nuke.curvelib.AnimControlPoint) -> None
        self.point = point
        self.center = center

        # implement AnimControlPoint interface
        self.removePositionKey = point.removePositionKey
        self.getPosition = self.abs_position
        self.addPositionKey = self.add_abs_position_key
        self.getControlPointKeyTimes = point.getControlPointKeyTimes

    def abs_position(self, frame):
        # type: (float) -> nuke.curvelib.CVec3
        return self.center.getPosition(frame) + self.point.getPosition(frame)

    def add_abs_position_key(self, frame, position):
        # type: (float, nuke.curvelib.CVec3) -> None
        self.point.addPositionKey(frame, position - self.center.getPosition(frame))
