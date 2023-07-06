# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Protocol

class LocalStorageService(Protocol):
    def __getitem__(
        self,
        key: Text,
        /,
    ) -> Text: ...
    def __setitem__(self, key: Text, value: Text, /) -> None: ...
    def __delitem__(self, key: Text) -> None: ...
