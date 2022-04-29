# -*- coding=UTF-8 -*-
# pyright: strict,reportUnusedImport=false
"""WuliFang plugin for Nuke and Hiero.  """

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any

    from .types import MessageService, PublishService

import os

from ._reload import reload as reload_modules


def _undefined():
    # type: () -> Any
    """used this to prevent type inference."""


# services
# should been set during init
message = _undefined()  # type: MessageService
publish = _undefined()  # type: PublishService
is_debug = os.getenv("DEBUG") == "wulifang"
