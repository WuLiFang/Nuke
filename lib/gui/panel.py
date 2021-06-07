# -*- coding=UTF-8 -*-
"""Addtional panels.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import cgtwq
import panels
import cast_unknown as cast

LOGGER = logging.getLogger(__name__)


def add_panel():
    """Add custom pannel."""

    LOGGER.info("添加面板")
    if cgtwq.DesktopClient().executable():
        import cgtwq_uploader

        panels.register(
            cgtwq_uploader.Dialog,
            cast.binary("上传mov"),
            b"com.wlf.uploader",
        )
