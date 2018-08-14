# -*- coding=UTF-8 -*-
"""Nuke dropdata enhancement.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
from itertools import chain

import pluggy

from wlf.codectools import get_unicode as u
from wlf.progress import CancelledError, progress

PROJECT_NAME = 'com.wlf.nuke.dropdata'
HOOKSPEC = pluggy.HookspecMarker(PROJECT_NAME)
HOOKIMPL = pluggy.HookimplMarker(PROJECT_NAME)

LOGGER = logging.getLogger(__name__)


def dropdata_handler(mime_type, data, hook):
    """Handling dropdata."""

    if mime_type != 'text/plain':
        return None
    data = u(data)
    if hook.is_ignore_data(data=data):
        return None

    LOGGER.debug('Handling dropdata: %s %s', mime_type, data)
    urls = chain([data], *hook.get_url(data=data))
    filenames = chain(
        *(chain([i], *hook.get_filenames(url=i)) for i in urls))

    try:
        ret = None
        for filename in progress(list(filenames)):
            if hook.is_ignore_filename(filename=filename):
                LOGGER.debug('Ignore filename: %s', filename)
                ret = True
                continue
            LOGGER.debug('Handling filename: %s', filename)
            context = {'is_created': False}
            nodes = chain(
                *hook.create_node(filename=filename, context=context))
            if any(nodes):
                ret = True
        return ret
    except CancelledError:
        return True
