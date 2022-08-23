# -*- coding=UTF-8 -*-
# pyright: strict,reportUnusedImport=false, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    import wulifang.types
    from . import types
    from typing import Any

from ._init import init
from ._reload import reload


def _undefined():
    # type: () -> Any
    """used this to prevent type inference."""


# cleanup before re-init
cleanup = _undefined()  # type: wulifang.types.CleanupService
publish = _undefined()  # type: wulifang.types.PublishService
active_viewer = _undefined()  # type: types.ActiveViewerService
callback = _undefined()  # type: types.CallbackService
file = _undefined()  # type: wulifang.types.FileService


def init_gui():
    from ._init_gui import init_gui

    init()
    init_gui()
