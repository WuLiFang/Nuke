# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text

import nuke
import os.path

import wulifang
from wulifang._util import cast_str, cast_text, workspace_path


def _obtain_menu(parent, name, icon):
    # type: (nuke.Menu, Text, Text) -> nuke.Menu
    name_str = cast_str(name)
    m = parent.menu(name_str)
    if isinstance(m, nuke.Menu):
        return m
    return parent.addMenu(name_str, icon=cast_str(icon))


class _Command(object):
    def __init__(self, node):
        # type: (Text) -> None
        self.node = node

    def create(self, menu):
        # type: (nuke.Menu) -> None

        node = cast_str(self.node)
        # not display version in menu
        name = self.node.rstrip("0123456789")
        cmd = menu.addCommand(
            cast_str(name),
            lambda: nuke.createNode(node),
            icon=cast_str("%s.png" % (name,)),
        )

        def cleanup():
            menu.removeItem(cmd.name())

        wulifang.cleanup.add(cleanup)


_DIR_IGNORE = ("Obsolete", "third_party")


def _render(parent, dir_):
    # type: (nuke.Menu, Text) -> None

    def order(name):
        # type: (Text) -> ...
        return (not os.path.isdir(os.path.join(dir_, name)), name)

    for i in sorted(os.listdir(dir_), key=order):
        i = cast_text(i)
        if i in _DIR_IGNORE:
            continue
        abspath = os.path.join(dir_, i)
        if os.path.isdir(abspath):
            m = nuke.menu(cast_str("Nodes")).findItem(cast_str(i)) or _obtain_menu(
                parent,
                i,
                "%s.svg" % (i,),
            )
            _render(m, abspath)
        else:
            name, ext = os.path.splitext(i)
            if ext.lower() == ".gizmo":
                _Command(name).create(parent)


def init_gui():
    # type: () -> None

    m = nuke.menu(cast_str("Nodes"))
    m = m.addMenu(cast_str("吾立方"), icon=cast_str("Modify.png"))
    _render(m, workspace_path("plugins"))
    _render(m, workspace_path("plugins", "third_party"))
