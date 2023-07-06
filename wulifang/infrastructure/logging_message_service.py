# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import wulifang

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text
    from .._types import MessageService


class LoggingMessageService:
    def __init__(self):
        # type: () -> None
        logger = logging.getLogger("wulifang")
        logger.setLevel(logging.DEBUG)
        self._logger = logger

    def debug(self, message, title=""):
        # type: (Text, Text) -> None
        if not wulifang.is_debug:
            return
        if title:
            message = "[%s] %s" % (title, message)
        self._logger.debug(message)

    def info(self, message, title=""):
        # type: (Text, Text) -> None
        if title:
            message = "[%s] %s" % (title, message)
        self._logger.info(message)

    def error(self, message, title=""):
        # type: (Text, Text) -> None
        if title:
            message = "[%s] %s" % (title, message)
        self._logger.error(message)


def _(v):
    # type: (LoggingMessageService) -> MessageService
    return v
