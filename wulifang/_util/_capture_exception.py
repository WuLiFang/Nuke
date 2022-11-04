# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from wulifang.types import MessageService
    from typing import Optional, Generator

import contextlib


def _default_message():
    import wulifang

    if wulifang.message is None:
        from wulifang.infrastructure.logging_message_service import (
            LoggingMessageService,
        )

        return LoggingMessageService()
    return wulifang.message


@contextlib.contextmanager
def capture_exception(message=None):
    # type: (Optional[MessageService]) -> Generator[None, None, None]
    message = message or _default_message()
    try:
        yield
    except Exception as ex:
        message.error("%s" % ex)
