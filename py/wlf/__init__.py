# -*- coding=UTF-8 -*-
"""wlf studio nuke plugins"""

import os

import nuke

from .comp import Comp
from . import asset, comp, pref, ui, callback, backdrop, csheet
try:
    from . import cgtwn
except ImportError:
    pass

__all__ = ['asset', 'comp', 'edit', 'csheet']
__version__ = '1.0.0'
