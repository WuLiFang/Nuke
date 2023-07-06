# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from wulifang._types import MessageService
    from typing import Text, Iterator, Optional


class MultiMessageService:
    @staticmethod
    def _iter(*services):
        # type: (Optional[MessageService]) -> Iterator[MessageService]
        for i in services:
            if i is None:
                continue
            if isinstance(i, MultiMessageService):
                for j in i._s:
                    yield j
            else:
                yield i

    def __init__(self, *services):
        # type: (Optional[MessageService]) -> None

        self._s = tuple(self._iter(*services))

    def info(self, message, title=""):
        # type: (Text, Text) -> None
        for i in self._s:
            i.info(message, title=title)

    def error(self, message, title=""):
        # type: (Text, Text) -> None
        for i in self._s:
            i.error(message, title=title)

    def debug(self, message, title=""):
        # type: (Text, Text) -> None
        for i in self._s:
            i.debug(message, title=title)


def _(v):
    # type: (MultiMessageService) -> MessageService
    return v
