"""The Python interface for Nuke's curve library (as used by
Roto, RotoPaint, SplineWarp).

Use help('_curvelib') to get detailed help on the classes exposed here.

This module provides the public interface to the curvelib module and will
remain stable. It uses an underlying native module called _curvelib to
provide this interface. While there is nothing stopping you from using the
_curvelib module directly, it may change in a future release and break your
scripts.
"""

import _curvelib

from _curvelib import AnimAttributes
from _curvelib import AnimCTransform
from _curvelib import AnimCurveViews
from _curvelib import CMatrix4
from _curvelib import CTransform
from _curvelib import CVec2
from _curvelib import CVec3
from _curvelib import CVec4
from _curvelib import ControlPoint
from _curvelib import CubicCurve
from _curvelib import AnimControlPoint
from _curvelib import AnimCurveKey
from _curvelib import BaseCurve
from _curvelib import AnimCurve
from _curvelib import Flag

# enums
from _curvelib import CurveType
from _curvelib import FlagType
from _curvelib import ExtrapolationType
from _curvelib import InterpolationType
from _curvelib import RotationOrder
from _curvelib import TransformOrder
