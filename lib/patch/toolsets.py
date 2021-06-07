# -*- coding=UTF-8 -*-
"""Patch nukescript toolset functions.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import webbrowser

import nuke
import nukescripts  # pylint: disable=import-error
import cast_unknown as cast

import filetools

from .core import BasePatch


class Patch(BasePatch):
    """Enhance toolsets menu."""

    target = "nukescripts.toolsets.refreshToolsetsMenu"

    @classmethod
    def func(cls, *args, **kwargs):

        cls.orig(*args, **kwargs)
        m = nuke.menu(b"Nodes").addMenu(b"ToolSets")
        _ = m.addCommand("刷新".encode("utf-8"), cls.func)
        _ = m.addCommand("创建共享工具集".encode("utf-8"), _create_shared_toolsets)
        _ = m.addCommand(
            "打开共享工具集文件夹".encode("utf-8"),
            lambda: webbrowser.open(filetools.plugin_folder_path("ToolSets", "Shared")),
        )

    @classmethod
    def enable(cls, is_strict=True):
        super(Patch, cls).enable(is_strict)
        cls.func()


def _create_shared_toolsets():
    if not nuke.selectedNodes():
        nuke.message("未选中任何节点,不能创建工具集".encode("utf-8"))
        return
    toolset_name = nuke.getInput(b"ToolSet name")
    if toolset_name:
        nuke.createToolset(
            filename=cast.binary("Shared/{}".format(toolset_name)),
            rootPath=cast.binary(filetools.plugin_folder_path()),
        )
    nukescripts.toolsets.refreshToolsetsMenu()


enable = Patch.enable  # pylint: disable=invalid-name
disable = Patch.disable  # pylint: disable=invalid-name
