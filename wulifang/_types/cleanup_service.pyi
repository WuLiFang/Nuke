# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import annotations
from typing import Callable, Protocol

Callback = Callable[[], None]
Cancel = Callable[[], None]

class CleanupService(Protocol):
    def add(self, cb: Callback) -> Cancel: ...
    def run(self) -> None: ...
