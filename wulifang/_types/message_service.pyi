# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import annotations

from typing import Protocol, Text

class MessageService(Protocol):
    def debug(self, message: Text, /, *, title: Text = ...) -> None: ...
    def info(self, message: Text, /, *, title: Text = ...) -> None: ...
    def error(self, message: Text, /, *, title: Text = ...) -> None: ...
