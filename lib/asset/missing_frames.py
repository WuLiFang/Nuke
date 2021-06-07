# -*- coding=UTF-8 -*-
"""Check missing frames for asset.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import time
from concurrent import futures

import six

import cast_unknown as cast
import filetools
from pathlib2_unicode import Path

_EXISTS_CACHE = dict()
LOGGER = logging.getLogger(__name__)


def exists(path, ttl=0):
    path = Path(cast.text(path))
    ttl = int(ttl)

    key = os.path.normcase(cast.text(path))
    now = time.time()
    if key in _EXISTS_CACHE and _EXISTS_CACHE[key][0] > now - ttl:
        return _EXISTS_CACHE[key][1]

    value = (now, path.exists())
    _EXISTS_CACHE[key] = value
    return value[1]


def get(filename, first, last, ttl=60):
    LOGGER.debug("get: %s", filename)

    ret = []
    with futures.ThreadPoolExecutor(8) as executor:
        for f, is_exist in executor.map(
            lambda f: (f, exists(filetools.expand_frame(filename, f), ttl)),
            six.moves.range(first, last + 1),
        ):
            if not is_exist:
                ret.append(f)
    return ret
