# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false
from __future__ import absolute_import, division, print_function, unicode_literals


import logging
import os
import sys

from wulifang.vendor.six.moves import reload_module
from wulifang._util import workspace_path, iteritems

import nuke

from .. import _reload  # type: ignore


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
    if path.startswith(os.path.normpath(workspace_path("lib"))):
        return True
    return False


def _reload_modules():
    _reload.reload()

    # reload legacy modules
    for k, v in iteritems(dict(sys.modules)):
        if v is None:  # type: ignore
            continue
        if k not in ("__main__",) and _is_legacy_plugin_module(v):
            try:
                reload_module(v)
            except:
                _LOGGER.exception("reload failed: %s", v)


def reload():
    # reload twice to ensure all module reloaded
    _reload_modules()
    _reload_modules()

    import wulifang.nuke

    wulifang.nuke.init()
    if nuke.GUI:
        wulifang.nuke.init_gui()
