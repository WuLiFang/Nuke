# -*- coding=UTF-8 -*-
"""Rotopaint scripting tools.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke.curveknob

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
        if isinstance(i, nuke.curveknob.Layer):
            for j in iter_layer(i):
                yield j


def iter_shapes_in_layer(layer):
    """Iterate shapes in layer recursively.

    Args:
        layer (nuke.rotopaint.Layer): The layer to iterate.

    Yields:
        Iterator[nuke.rotopaint.Shape]: shapes in layer.
    """
    for i in iter_layer(layer):
        if isinstance(i, nuke.curveknob.Shape):
            yield i


class PointProxy(object):
    """Abstract proxy for nuke.rotopaint.AnimControlPoint. """

    def __init__(self, point):
        self.point = point

    def __getattr__(self, name):
        return getattr(self.point, name)


class RelativePointProxy(PointProxy):
    """
    RelativePointProxy change point methods
    to work with absolute position.
    """

    def __init__(self, point, center):
        super(RelativePointProxy, self).__init__(point)
        self.center = center

    def getPosition(self, frame):
        return self.center.getPosition(frame) + self.point.getPosition(frame)

    def addPositionKey(self, frame, position):
        self.point.addPositionKey(
            frame, position-self.center.getPosition(frame))


def iter_shape_point(point):
    """Iterate AnimControlPoint in given shape point,
    Relative point is wrapped with RelativePointProxy
    so we can treat all points as absolute.

    Args:
        point (nuke.rotopaint.ShapeControlPoint): The point to iterate.

    Yields:
        Iterator[Union[nuke.rotopaint.AnimControlPoint, RelativePointProxy]]:
            items in point.
    """

    # type: (nuke.rotopaint.ShapeControlPoint,)
    # -> Iterator[Union[nuke.rotopaint.AnimControlPoint, RelativePointProxy]]
    yield point.center
    yield RelativePointProxy(point.leftTangent, point.center)
    yield RelativePointProxy(point.rightTangent, point.center)
    yield RelativePointProxy(point.featherCenter, point.center)
    yield RelativePointProxy(point.featherLeftTangent, point.center)
    yield RelativePointProxy(point.featherRightTangent, point.center)
