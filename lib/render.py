# -*- coding=UTF-8 -*-
"""Convert gizmo to group.  """


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import os
import re
import sys

import nuke

import callback
from node import wlf_write_node
from wlf.codectools import get_encoded as e
from wlf.codectools import get_unicode as u
from wlf.fileutil import map_drivers

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


def disable_precomp_hashcheck():
    """Disable annoying hashcheck that can not disable by panel.  """

    precomp_write_nodes = [
        n for i in nuke.allNodes('Precomp', group=nuke.Root())
        for n in nuke.allNodes('Write', group=i)]
    nuke.tprint('testiing: precomp: {}'.format(len(precomp_write_nodes)))
    for n in precomp_write_nodes:
        n['checkHashOnRead'].setValue(False)


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
    if sys.platform == 'win32':
        if re.match(r'(?i)wlf(\d+|\b)', os.getenv('ComputerName')):
            map_drivers()

    callback.CALLBACKS_ON_SCRIPT_SAVE.append(_jump_frame)
    callback.CALLBACKS_BEFORE_RENDER.append(create_out_dirs)
    callback.CALLBACKS_BEFORE_RENDER.append(disable_precomp_hashcheck)
