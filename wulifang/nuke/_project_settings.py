# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none
"""Set project automatically.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import os

import nuke

import wulifang.nuke
from wulifang._util import cast_str, cast_text
from wulifang.nuke._util import (
    knob_of,
    ignore_modification,
)


def _eval_proj_dir():
    if nuke.numvalue(cast_str("preferences.wlf_eval_proj_dir"), 0.0):
        attr = cast_str("root.project_directory")
        nuke.knob(
            attr,
            cast_str(os.path.abspath(cast_text(nuke.value(attr))).replace("\\", "/")),
        )


def _add_root_info():
    """add info to root."""

    artist = nuke.value(cast_str("preferences.wlf_artist"), cast_str(""))
    if not artist:
        return
    if not nuke.exists(cast_str("root.wlf")):
        n = nuke.Root()
        k = nuke.Tab_Knob(cast_str("wlf"), cast_str("吾立方"))
        k.setFlag(nuke.STARTLINE)
        n.addKnob(k)

        k = nuke.String_Knob(cast_str("wlf_artist"), cast_str("制作人"))
        k.setFlag(nuke.STARTLINE)
        k.setValue(artist)
        n.addKnob(k)
    else:
        if nuke.exists(cast_str("root.wlf_artist")) and not nuke.value(
            cast_str("root.wlf_artist"), cast_str("")
        ):
            nuke.knob(cast_str("root.wlf_artist"), artist)


def _lock_connections():
    root = nuke.root()
    if nuke.numvalue(cast_str("preferences.wlf_lock_connections"), 0.0):
        with ignore_modification():
            knob_of(root, "lock_connections", nuke.Boolean_Knob).setValue(True)


def _check_project():
    project_directory = cast_text(nuke.value(cast_str("root.project_directory")))
    if not project_directory:
        _name = cast_text(nuke.value(cast_str("root.name"), cast_str("")))
        if _name:
            _dir = os.path.dirname(_name)
            nuke.knob(cast_str("root.project_directory"), cast_str(_dir))
            nuke.message(cast_str("工程目录未设置, 已自动设为: {}".format(_dir)))
        else:
            nuke.message(cast_str("工程目录未设置"))
    # avoid ValueError of script_directory() when no root.name.
    elif project_directory == (
        r"[python {os.path.abspath(os.path.join("
        r"'D:/temp', nuke.value(b'root.name', ''), '../'"
        r")).replace('\\', '/')}]"
    ):
        nuke.knob(
            cast_str("root.project_directory"),
            cast_str(
                r"[python {os.path.join("
                r"nuke.value(b'root.name', ''), '../'"
                r").replace('\\', '/')}]"
            ),
        )


def init_gui():
    wulifang.nuke.callback.on_script_load(_add_root_info)
    wulifang.nuke.callback.on_script_load(_eval_proj_dir)
    wulifang.nuke.callback.on_script_save(_lock_connections)
    wulifang.nuke.callback.on_script_save(_check_project)
