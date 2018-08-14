# -*- coding=UTF-8 -*-
"""Drop data plguins.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import (anyfile, cut_paste_ignore, deep_exr, directory, fbx,
               file_protocol, nk, vector_field, win_ignore)

ALL = [directory, win_ignore, file_protocol,
       deep_exr, anyfile, fbx, nk, vector_field, cut_paste_ignore]
