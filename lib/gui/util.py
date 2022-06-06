# -*- coding=UTF-8 -*-
"""Gui util.  """

from __future__ import absolute_import, division, print_function, unicode_literals

from .callback_ import add_callback
from .menu import add_menu
from .panel import add_panel


def setup():
    """Setup ui."""

    add_menu()
    add_panel()
    add_callback()
