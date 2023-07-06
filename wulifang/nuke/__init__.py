# -*- coding=UTF-8 -*-
# pyright: strict,reportUnusedImport=false, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    import wulifang._types
    from . import _types
    from typing import Any

from ._init import init
from ._reload import reload


def _undefined():
    # type: () -> Any
    """used this to prevent type inference."""


# cleanup before re-init
publish = _undefined()  # type: wulifang._types.PublishService
active_viewer = _undefined()  # type: _types.ActiveViewerService
callback = _undefined()  # type: _types.CallbackService
file = _undefined()  # type: wulifang._types.FileService


def init_gui():
    from ._init_gui import init_gui

    init()
    init_gui()
