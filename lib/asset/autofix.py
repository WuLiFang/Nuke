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
    """Try fix all nodes that has filename error."""

    def _current_basename(filename):
        if not filename:
            return None
        return PurePath(filename).with_frame(nuke.frame()).name

    filename_dict = {}

    def _update_map(filename):
        if not filename:
            return
        filename_dict[_current_basename(filename)] = filename

    _ = [_update_map(nuke.filename(n))
         for n in nuke.allNodes() if not n.hasError()]

    result = {'success': 0, 'fail': 0}
    for n in nuke.allNodes():
        try:
            if not n.hasError() or n['disable'].value():
                continue
        except NameError:
            continue

        filename = nuke.filename(n)
        if not filename:
            continue

        is_fixed = False
        new_path = filename_dict.get(_current_basename(filename))
        if os.path.basename(filename).lower() == 'thumbs.db':
            nuke.delete(n)
            is_fixed = True
        elif new_path:
            _set_filename(n, new_path)
            is_fixed = True
        else:
            is_fixed = dropdata_handler('text/plain', filename)

        result['success' if is_fixed else 'fail'] += 1

    nuke.message('成功修复 {success} 个节点, 失败 {fail} 个'.format(
        **result).encode('utf-8'))


def _set_filename(n, value):
    try:
        k = (n['file'] if not n['proxy'].value()
             or nuke.value('root.proxy') == 'false' else n['proxy'])
    except NameError:
        k = n['file']
    k.setValue(value)
