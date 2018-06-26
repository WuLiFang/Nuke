# -*- coding=UTF-8 -*-
"""Addtional panels.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

import cgtwq_uploader

import panels

LOGGER = logging.getLogger(__name__)


def add_panel():
    """Add custom pannel. """

    LOGGER.info('添加面板')
    panels.register(cgtwq_uploader.Dialog, '上传mov', 'com.wlf.uploader')
