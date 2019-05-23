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

        client = cgtwq.DesktopClient()
        if not client.executable():
            return

        import cgtwn
        import pyblish_lite_nuke
        import time

        started = time.clock()
        while time.clock() - started < 10:
            try:
                client.start()
                pyblish_lite_nuke.setup()
                cgtwn.setup()
                if client.is_logged_in():
                    client.connect()
                break
            # pylint: disable=bare-except
            except:
                import traceback
                traceback.print_exc()

    _setup_cgtw()
    gui.setup()
    pref.setup()
    dropdata.setup()
    gizmo_convert.setup()
    project_settings.setup()
    enable_later.setup()
    asset.setup()

    patch.toolsets.enable()


if __name__ == '__main__':
    main()
    del main  # Clean namespace for script editor.
