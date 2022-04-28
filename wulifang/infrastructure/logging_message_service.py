# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text
    from ..types import MessageService


import logging


class LoggingMessageService:
    def __init__(self):
        # type: () -> None
        logger = logging.Logger("wulifang", logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(levelname)-6s[%(asctime)s]%(name)s: %(message)s",
            "%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self._logger = logger

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
