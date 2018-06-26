# -*- coding=UTF-8 -*-
"""Auto fix wrong nodes.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import os

import nuke

from wlf.path import PurePath

from .dropdata import dropdata_handler

LOGGER = logging.getLogger(__name__)


def fix_read():
    """Try fix all read nodes that has error."""

    def _get_name(filename):
        return PurePath(filename).name

    filename_dict = {_get_name(nuke.filename(n)): nuke.filename(n)
                     for n in nuke.allNodes('Read') if not n.hasError()}
    for n in nuke.allNodes('Read'):
        if not n.hasError() or n['disable'].value():
            continue
        fix_result = None
        filename = nuke.filename(n)
        name = os.path.basename(nuke.filename(n))
        new_path = filename_dict.get(_get_name(name))
        if os.path.basename(filename).lower() == 'thumbs.db':
            fix_result = True
        elif new_path:
            filename_knob = n['file'] if not n['proxy'].value() \
                or nuke.value('root.proxy') == 'false' else n['proxy']
            filename_knob.setValue(new_path)
        else:
            fix_result = dropdata_handler('text/plain', filename)
        if fix_result:
            nuke.delete(n)
