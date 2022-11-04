# -*- coding=UTF-8 -*-
# pyright: strict,reportUnusedImport=false,reportTypeCommentUsage=false
"""WuliFang plugin for Nuke and Hiero.  """

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any

    from .types import MessageService, PublishService, FileService, ManifestService

import os

from ._reload import reload as reload_modules
from .infrastructure.no_op_publish_service import (
    NoOpPublishService as _DefaultPublishService,
)
from .infrastructure.file_service import FileService as _DefaultFileService
from .infrastructure.logging_message_service import (LoggingMessageService as _DefaultMessageService)

def _undefined():
    # type: () -> Any
    """used this to prevent type inference."""


# services
# should been set during init
message = _undefined()  # type: MessageService
publish = _undefined()  # type: PublishService
file = _undefined()  # type: FileService
manifest = _undefined()  # type: ManifestService
is_debug = os.getenv("DEBUG") == "wulifang"

publish = _DefaultPublishService()
file = _DefaultFileService()
message =  _DefaultMessageService()
