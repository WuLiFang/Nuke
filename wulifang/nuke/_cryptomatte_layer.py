# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


class CryptomatteLayer:
    def __init__(self, id, metadata):
        # type: (Text, dict[Text,Text]) -> None
        self.id = id
        self.metadata = metadata

    def name(self):
        return self.metadata["name"]
