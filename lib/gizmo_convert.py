# -*- coding=UTF-8 -*-
"""Convert gizmo to group.  """


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

import callback
import edit
import cast_unknown as cast


def _gizmo_to_group_on_create():
    n = nuke.thisNode()
    if not nuke.numvalue(b'preferences.wlf_gizmo_to_group', 0.0):
        return

    if not isinstance(n, nuke.Gizmo):
        return

    # Avoid scripted gizmo.
    if nuke.knobChangeds.get(n.Class()):
        return

    n.addKnob(nuke.Text_Knob(b'wlf_gizmo_to_group'))


def _gizmo_to_group_update_ui():
    n = nuke.thisNode()
    _temp_knob_name = 'wlf_gizmo_to_group'
    _has_temp_knob = nuke.exists(
        cast.binary('{}.{}'.format(cast.text(n.name()), _temp_knob_name)))

    if _has_temp_knob:
        n = edit.gizmo_to_group(n)
        n.removeKnob(n[cast.binary(_temp_knob_name)])
        n.removeKnob(n[b'User'])


def setup():
    """Setup gizmo auto convert.   """

    callback.CALLBACKS_ON_CREATE.append(_gizmo_to_group_on_create)
    callback.CALLBACKS_UPDATE_UI.append(_gizmo_to_group_update_ui)
