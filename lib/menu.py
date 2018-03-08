# -*- coding: UTF-8 -*-
"""Nuke menu file."""

from __future__ import absolute_import

import _ui
import callback
import pref
from wlf import cgtwq, uitools
import os

import pyblish_lite_nuke


def main():
    """Main entry.  """

    _ui.add_menu()
    _ui.add_panel()
    _ui.add_autolabel()
    pref.add_preferences()
    pref.set_knob_default()

    pyblish_lite_nuke.setup()

    if cgtwq.MODULE_ENABLE:
        cgtwq.CGTeamWork.update_status()


if __name__ == '__main__':
    main()
