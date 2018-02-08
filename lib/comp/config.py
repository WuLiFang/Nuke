# -*- coding=UTF-8 -*-
""" Config object for module.  """

from __future__ import absolute_import, print_function, unicode_literals

import os

from wlf.config import Config


START_MESSAGE = '{:-^50s}'.format('COMP START')

# bitmask
IGNORE_EXISTED = 1 << 0
MULTI_THREADING = 1 << 1


class CompConfig(Config):
    """Comp config.  """

    default = {
        'fps': 25,
        'footage_pat': r'^.+\.exr[0-9\- ]*$',
        'tag_pat':
        r'(?i)(?:[^_]+_)?(?:ep\d+_)?(?:\d+[a-zA-Z]*_)?'
        r'(?:sc\d+[a-zA-Z]*_)?((?:[a-zA-Z][^\._]*_?){,2})',
        'mp': r"Z:\SNJYW\MP\EP14\MP_EP14_1.nk",
        'precomp': True,
        'masks': True,
        'colorcorrect': True,
        'filters': True,
        'zdefocus': True,
        'depth': True,
        'other': True,
    }
    path = os.path.expanduser('~/.nuke/wlf.comp.json')


class BatchCompConfig(Config):
    """BatchComp config.  """

    default = {
        'dir_pat': r'^.{4,}$',
        'output_dir': 'E:/precomp',
        'input_dir': 'Z:/SNJYW/Render/EP',
        'txt_name': '镜头备注',
        'exclude_existed': True,
    }
    path = os.path.expanduser(u'~/.nuke/wlf.batchcomp.json')
