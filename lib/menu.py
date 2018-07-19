# -*- coding: UTF-8 -*-
"""Nuke menu file."""

from __future__ import absolute_import


def main():
    import gui
    import dropdata_handler
    import gizmo_convert
    import pref
    import project_settings
    # import pyblish_lite_nuke
    # import cgtwn
    # import cgtwq
    import enable_later
    import asset

    gui.setup()
    pref.setup()
    dropdata_handler.setup()
    gizmo_convert.setup()
    project_settings.setup()
    enable_later.setup()
    asset.setup()
    # cgtwn.setup()
    # cgtwq.DesktopClient.start()
    # if cgtwq.DesktopClient.is_logged_in():
    #     cgtwq.update_setting()
    # pyblish_lite_nuke.setup()


if __name__ == '__main__':
    main()
    del main  # Clean namespace for script editor.
