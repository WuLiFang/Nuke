# -*- coding=UTF-8 -*-
"""Set project automatically.  """


from __future__ import absolute_import, division, print_function, unicode_literals

import os

import wulifang.nuke
import wulifang.vendor.cast_unknown as cast

import nuke


def _eval_proj_dir():
    if nuke.numvalue(b"preferences.wlf_eval_proj_dir", 0.0):
        attr = b"root.project_directory"
        nuke.knob(attr, os.path.abspath(nuke.value(attr)).replace(b"\\", b"/"))


def _add_root_info():
    """add info to root."""

    artist = nuke.value(b"preferences.wlf_artist", b"")
    if not artist:
        return
    if not nuke.exists(b"root.wlf"):
        n = nuke.Root()
        k = nuke.Tab_Knob(b"wlf", cast.binary("吾立方"))
        k.setFlag(nuke.STARTLINE)
        n.addKnob(k)

        k = nuke.String_Knob(b"wlf_artist", cast.binary("制作人"))
        k.setFlag(nuke.STARTLINE)
        k.setValue(artist)
        n.addKnob(k)
    else:
        if nuke.exists(b"root.wlf_artist") and not nuke.value(b"root.wlf_artist", b""):
            nuke.knob(b"root.wlf_artist", artist)


def _lock_connections():
    if nuke.numvalue(b"preferences.wlf_lock_connections", 0.0):
        _ = nuke.Root()[b"lock_connections"].setValue(1)
        nuke.Root().setModified(False)


def _check_project():
    project_directory = nuke.value(b"root.project_directory")
    if not project_directory:
        _name = nuke.value(b"root.name", b"")
        if _name:
            _dir = os.path.dirname(_name)
            nuke.knob(b"root.project_directory", _dir)
            nuke.message(cast.binary("工程目录未设置, 已自动设为: {}".format(_dir)))
        else:
            nuke.message(cast.binary("工程目录未设置"))
    # avoid ValueError of script_directory() when no root.name.
    elif (
        project_directory == r"[python {os.path.abspath(os.path.join("
        r"'D:/temp', nuke.value(b'root.name', ''), '../'"
        r")).replace('\\', '/')}]"
    ):
        nuke.knob(
            b"root.project_directory",
            cast.binary(
                r"[python {os.path.join("
                r"nuke.value(b'root.name', ''), '../'"
                r").replace('\\', '/')}]"
            ),
        )


def init():
    wulifang.nuke.callback.on_script_load(_add_root_info)
    wulifang.nuke.callback.on_script_load(_eval_proj_dir)
    wulifang.nuke.callback.on_script_save(_lock_connections)
    wulifang.nuke.callback.on_script_save(_check_project)
