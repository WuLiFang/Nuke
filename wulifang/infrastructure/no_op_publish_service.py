# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:

    from ..types import PublishService


class NoOpPublishService:
    def validate(self):
        pass

    def request_validate(self):
        pass

    def publish(self):
        pass


def _(v):
    # type: (NoOpPublishService) -> PublishService
    return v
