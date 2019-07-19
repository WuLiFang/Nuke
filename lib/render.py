# -*- coding=UTF-8 -*-
"""Convert gizmo to group.  """


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import os

import nuke

import callback
from node import wlf_write_node
from wlf.codectools import get_encoded as e
from wlf.codectools import get_unicode as u

LOGGER = logging.getLogger('wlf.render')


def create_out_dirs(node=None):
    """Create this read node's output dir if need."""

    n = node or nuke.thisNode()
    try:
        if n['disable'].value():
            return
    except NameError:
        pass

    filename = u(nuke.filename(n))
    if filename:
        target_dir = e(os.path.dirname(filename))
        if not os.path.isdir(target_dir):
            LOGGER.debug('Create dir: %s', target_dir)
            os.makedirs(target_dir)


def _jump_frame():
    if nuke.numvalue('preferences.wlf_jump_frame', 0.0):
        LOGGER.debug('Jump frame')
        try:
            n = wlf_write_node()
        except ValueError:
            LOGGER.warning('No `wlf_Write` node.')
            return
        if n:
            nuke.frame(n['frame'].value())
            nuke.Root().setModified(False)


def setup():
    callback.CALLBACKS_ON_SCRIPT_SAVE.append(_jump_frame)
    callback.CALLBACKS_BEFORE_RENDER.append(create_out_dirs)
