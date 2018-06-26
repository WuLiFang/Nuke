# -*- coding: UTF-8 -*-
"""Nuke menu file."""

from __future__ import absolute_import


def main():
    import gui
    import dropdata_handler
    import gizmo_convert
    import pref
    import project_settings
    import pyblish_lite_nuke
    import cgtwn
    import cgtwq
    import enable_later
    import asset

    gui.setup()
    pref.setup()
    dropdata_handler.setup()
    gizmo_convert.setup()
    project_settings.setup()
    pyblish_lite_nuke.setup()
    enable_later.setup()
    cgtwn.setup()
    cgtwq.DesktopClient.start()
    asset.setup()
    if cgtwq.DesktopClient.is_logged_in():
        cgtwq.update_setting()


if __name__ == '__main__':
    main()
    del main  # Clean namespace for script editor.
