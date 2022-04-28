# -*- coding=UTF-8 -*-
# pyright: strict,reportUnusedImport=false
"""WuliFang plugin for Nuke and Hiero.  """

from __future__ import absolute_import, division, print_function, unicode_literals


from ._reload import reload as reload_modules

TYPE_CHECKING = False
if TYPE_CHECKING:
    from .types import MessageService
    from typing import Any


def _undefined():
    # type: () -> Any
    """used this to prevent type inference."""


# services
# should been set during init
message = _undefined()  # type: MessageService
