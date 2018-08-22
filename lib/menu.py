# -*- coding: UTF-8 -*-
"""Nuke menu file."""

from __future__ import absolute_import


def main():
    import gui
    import dropdata
    import gizmo_convert
    import pref
    import project_settings
    import cgtwq
    import enable_later
    import asset
    import patch.toolsets

    def _setup_cgtw():
        import cgtwn
        import pyblish_lite_nuke

        cgtwq.DesktopClient.start()
        pyblish_lite_nuke.setup()
        cgtwn.setup()
        if cgtwq.DesktopClient.is_logged_in():
            cgtwq.update_setting()

    gui.setup()
    pref.setup()
    dropdata.setup()
    gizmo_convert.setup()
    project_settings.setup()
    enable_later.setup()
    asset.setup()
    if cgtwq.DesktopClient.executable():
        _setup_cgtw()

    patch.toolsets.enable()


if __name__ == '__main__':
    main()
    del main  # Clean namespace for script editor.
