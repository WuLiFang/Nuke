# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false
from __future__ import absolute_import, division, print_function, unicode_literals


import logging
import os
import sys

from wulifang.vendor.six import itervalues
from wulifang.vendor.six.moves import reload_module

import nuke

from .. import _reload  # type: ignore
from .. import pathtools

_LOGGER = logging.getLogger(__name__)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from types import ModuleType


def _is_legacy_plugin_module(module):
    # type: (ModuleType) -> bool
    if not hasattr(module, "__file__"):
        return False
    path = module.__file__
    if not path:
        return False
    if "site-packages" in path:
        return False
    path = os.path.normpath(path)
    if path.startswith(os.path.normpath(pathtools.workspace("lib"))):
        return True
    return False


def _reload_once():
    _reload.reload()

    # reload legacy modules
    for v in itervalues(dict(sys.modules)):
        if v is None:
            continue
        if _is_legacy_plugin_module(v):
            try:
                _ = reload_module(v)
            except:
                _LOGGER.exception("reload failed: %s", v)

    import wulifang.nuke

    wulifang.nuke.init()
    if nuke.GUI:
        wulifang.nuke.init_gui()


def reload():
    # reload twice to ensure all module reloaded
    _reload_once()
    _reload_once()
