# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import sys

import wulifang
from wulifang.infrastructure.logging_message_service import LoggingMessageService
from wulifang.infrastructure.multi_message_service import MultiMessageService
from wulifang.vendor.six import itervalues
from wulifang.vendor.six.moves import reload_module

import nuke

from .. import _reload  # type: ignore
from .. import pathtools

_LOGGER = logging.getLogger(__name__)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from types import ModuleType


class _g:
    init_once = False


def init():
    if _g.init_once:
        return

    wulifang.message = MultiMessageService(
        wulifang.message,
        LoggingMessageService(),
    )

    _g.init_once = True


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


def reload():
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
    init()
    if nuke.GUI:
        from ._init_gui import init_gui

        init_gui()
