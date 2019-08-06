# -*- coding=UTF-8 -*-
"""cache for asset status check.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

import six

import callback
from executor import EXECUTOR

_EXIST_CACHE = {}


def _update_exist_cache(key):
    _EXIST_CACHE[key] = os.path.exists(key)
    return _EXIST_CACHE[key]


def is_file_exist(path, timeout=-1):
    """Check file existence

    Args:
        path (string): file path

    Returns:
        Optional[bool] : null when no result in cache.
    """
    normalized_path = os.path.normcase(six.text_type(path))
    if not _EXIST_CACHE.has_key(normalized_path):
        future = EXECUTOR.submit(_update_exist_cache, normalized_path)
        if timeout > 0:
            return future.result(timeout)
        return None
    return _EXIST_CACHE.get(normalized_path)


def clear():
    """Clear cache.  """
    _EXIST_CACHE.clear()


def setup():
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(clear)
