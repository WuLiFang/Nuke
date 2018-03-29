# -*- coding=UTF-8 -*-
"""Set project automatically.  """


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

import nuke

import callback


def _eval_proj_dir():
    if nuke.numvalue('preferences.wlf_eval_proj_dir', 0.0):
        attr = 'root.project_directory'
        nuke.knob(attr, os.path.abspath(nuke.value(attr)).replace('\\', '/'))


def _add_root_info():
    """add info to root.  """

    artist = nuke.value('preferences.wlf_artist', '')
    if not artist:
        return
    if not nuke.exists('root.wlf'):
        n = nuke.Root()
        k = nuke.Tab_Knob('wlf', b'吾立方')
        k.setFlag(nuke.STARTLINE)
        n.addKnob(k)

        k = nuke.String_Knob('wlf_artist', b'制作人')
        k.setFlag(nuke.STARTLINE)
        k.setValue(artist)
        n.addKnob(k)
    else:
        if nuke.exists('root.wlf_artist') and not nuke.value('root.wlf_artist', ''):
            nuke.knob('root.wlf_artist', artist)


def _lock_connections():
    if nuke.numvalue('preferences.wlf_lock_connections', 0.0):
        nuke.Root()['lock_connections'].setValue(1)
        nuke.Root().setModified(False)


def _check_project():
    project_directory = nuke.value('root.project_directory')
    if not project_directory:
        _name = nuke.value('root.name', '')
        if _name:
            _dir = os.path.dirname(_name)
            nuke.knob('root.project_directory', _dir)
            nuke.message(b'工程目录未设置, 已自动设为: {}'.format(_dir))
        else:
            nuke.message(b'工程目录未设置')
    # avoid ValueError of script_directory() when no root.name.
    elif project_directory == r"[python {os.path.abspath(os.path.join("\
        r"'D:/temp', nuke.value('root.name', ''), '../'"\
            r")).replace('\\', '/')}]":
        nuke.knob('root.project_directory',
                  r"[python {os.path.join("
                  r"nuke.value('root.name', ''), '../'"
                  r").replace('\\', '/')}]")


def setup():
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(_add_root_info)
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(_eval_proj_dir)
    callback.CALLBACKS_ON_SCRIPT_SAVE.append(_lock_connections)
    callback.CALLBACKS_ON_SCRIPT_SAVE.append(_check_project)
