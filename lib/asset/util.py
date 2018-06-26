# -*- coding=UTF-8 -*-
"""Asset utility.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import callback

from . import localization
from .notify import warn_missing_frames, warn_mtime


def setup():
    localization.setup()

    callback.CALLBACKS_ON_SCRIPT_LOAD.append(warn_missing_frames)
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(warn_mtime)
    callback.CALLBACKS_ON_SCRIPT_SAVE.append(warn_missing_frames)
