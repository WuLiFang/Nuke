# -*- coding=UTF-8 -*-
"""Offset read node to match project settings.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

import nuke

from ..core import HOOKIMPL

# pylint: disable=missing-docstring

LOGGER = logging.getLogger(__name__)


@HOOKIMPL
def after_created(nodes):
    first_frame = nuke.numvalue('root.first_frame')
    # Skip when no need to offset frame range.
    if first_frame == 1:
        return

    read_nodes = [i for i in nodes
                  if i.Class() == 'Read'
                  and _is_reading_video(i)]

    for n in read_nodes:
        n['frame_mode'].setValue('start_at'.encode('utf-8'))
        n['frame'].setValue('{:.0f}'.format(first_frame).encode('utf-8'))


def _is_reading_video(node):
    first, last = node['first'].value(), node['last'].value()
    return first != last and first == 1
