# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text
    from ..types import MessageService

import logging

import wulifang

from wulifang.vendor import win_unicode_console


class LoggingMessageService:
    def __init__(self):
        # type: () -> None
        win_unicode_console.enable()
        logger = logging.Logger("wulifang", logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(levelname)-6s[%(asctime)s]%(name)s: %(message)s",
            "%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
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
