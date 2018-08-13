# -*- coding=UTF-8 -*-
"""Deep EXR file handle.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

from ..core import HOOKIMPL

# pylint: disable=missing-docstring


@HOOKIMPL
def create_node(filename, context):
    if not filename.lower().endswith('.exr'):
        return None
    n = nuke.nodes.DeepRead()
    n['file'].fromUserText(filename.encode('utf-8'))
    if n.hasError():
        nuke.delete(n)
        return None
    context['is_created'] = True
    return [n]
