# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import absolute_import, division, print_function, unicode_literals

from wulifang.vendor.six.moves import reload_module
from wulifang.vendor.six import iteritems

import sys

import logging

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import List
    from types import ModuleType


_LOGGER = logging.getLogger(__name__)


def reload():
    """reload wulifang modules."""
    modules = []  # type: List[ModuleType]
    for k, v in iteritems(sys.modules):
        if v is None:
            continue

        if k == "wulifang" or (
            k.startswith("wulifang.") and not k.startswith("wulifang.vendor")
        ):
            modules.append(v)
    for i in modules:
        try:
            _ = reload_module(i)
        except:
            _LOGGER.exception("reload failed: %s", i.__name__)
