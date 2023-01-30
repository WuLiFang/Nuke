# -*- coding: UTF-8 -*-
"""Nuke menu file."""

from __future__ import absolute_import


def main():
    import gui
    import dropdata
    import gizmo_convert
    import enable_later
    import asset
    import patch.toolsets

    gui.setup()
    dropdata.setup()
    gizmo_convert.setup()
    enable_later.setup()
    asset.setup()

    patch.toolsets.enable()


if __name__ == "__main__":
    main()
    del main  # Clean namespace for script editor.
