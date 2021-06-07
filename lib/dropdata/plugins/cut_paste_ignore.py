# -*- coding=UTF-8 -*-
"""Ignore cut paste data.  """

from __future__ import absolute_import, division, print_function, unicode_literals

from ..core import HOOKIMPL

# pylint: disable=missing-docstring


@HOOKIMPL
def is_ignore_data(data):
    if "\n" in data:
        return True
    return None
