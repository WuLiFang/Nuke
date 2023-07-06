"""The Python interface for Nuke's curve library (as used by
Roto, RotoPaint, SplineWarp).

Use help('_curvelib') to get detailed help on the classes exposed here.

This module provides the public interface to the curvelib module and will
remain stable. It uses an underlying native module called _curvelib to
provide this interface. While there is nothing stopping you from using the
_curvelib module directly, it may change in a future release and break your
scripts.
"""

from _curvelib import *
