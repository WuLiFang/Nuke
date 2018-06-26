# -*- coding=UTF-8 -*-
"""Modify nuke localization functionality.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
from functools import wraps

import nuke

import callback

LOGGER = logging.getLogger(__name__)


def is_support_localization():
    """Return is nuke supported localization feature.  """

    return nuke.env['NukeVersionMajor'] < 10


def need_localization_support(func):
    """Decorator.  """

    @wraps(func)
    def _func(*args, **kwargs):
        if not is_support_localization():
            return
        func(*args, **kwargs)

    return _func


@need_localization_support
def update():
    """Update localized files"""

    LOGGER.info('清理素材缓存')
    import nuke.localization as l10n
    l10n.clearUnusedFiles()
    l10n.pauseLocalization()
    l10n.forceUpdateAll()
    l10n.setAlwaysUseSourceFiles(True)


def setup():
    if not nuke.GUI or not is_support_localization():
        return
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(update)
