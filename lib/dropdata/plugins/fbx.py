# -*- coding=UTF-8 -*-
"""Fbx file handle.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

from ..core import HOOKIMPL
import cast_unknown as cast
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
    n.setName(b'Camera_3DEnv_1')
    cast.instance(n[b'file'], nuke.File_Knob).fromUserText(filename.encode('utf-8'))
    if nuke.expression('{}.animated'.format(n.name())):
        _ = n[b'read_from_file'].setValue(False)
    else:
        nuke.delete(n)
        n = nuke.nodes.ReadGeo2()
        cast.instance(n[b'file'], nuke.File_Knob).fromUserText(filename.encode('utf-8'))
        _ = n[b'all_objects'].setValue(True)
    if n.hasError():
        nuke.delete(n)
        return None
    context['is_created'] = True
    return [n]
