# -*- coding=UTF-8 -*-
"""Gui callbacks.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

import callback
import edit


def add_callback():
    """Register callbacks."""

    callback.CALLBACKS_ON_CREATE.append(
        lambda: edit.set_random_glcolor(nuke.thisNode())
    )
