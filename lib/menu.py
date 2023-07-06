# -*- coding: UTF-8 -*-
"""Nuke menu file."""

from __future__ import absolute_import


def main():
    import gui

    gui.setup()


if __name__ == "__main__":
    main()
    del main  # Clean namespace for script editor.
