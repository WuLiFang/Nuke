# -*- coding=UTF-8 -*-
"""Fbx file handle.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

from ..core import HOOKIMPL

# pylint: disable=missing-docstring


@HOOKIMPL
def create_node(filename, context):
    if not filename.lower().endswith('.fbx'):
        return None

    n = nuke.nodes.Camera2(read_from_file=True,
                           frame_rate=25,
                           suppress_dialog=True,
                           label='导入的摄像机：\n'
                           '[basename [value file]]\n'.encode('utf-8'))
    n.setName('Camera_3DEnv_1')
    n['file'].fromUserText(filename.encode('utf-8'))
    if nuke.expression('{}.animated'.format(n.name())):
        n['read_from_file'].setValue(False)
    else:
        nuke.delete(n)
        n = nuke.nodes.ReadGeo2()
        n['file'].fromUserText(filename.encode('utf-8'))
        n['all_objects'].setValue(True)
    if n.hasError():
        nuke.delete(n)
        return None
    context['is_created'] = True
    return [n]
