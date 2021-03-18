# -*- coding=UTF-8 -*-
"""Deep EXR file handle.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

from ..core import HOOKIMPL

# pylint: disable=missing-docstring


@HOOKIMPL
def create_node(filename, context):
    if not filename.lower().endswith('.vf'):
        return None
    n = nuke.nodes.Vectorfield(
        vfield_file=filename.encode('utf-8'),
        file_type='vf',
        label=b'[value this.vfield_file]'
    )
    context['is_created'] = True
    return [n]
