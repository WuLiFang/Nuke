# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
from typing import Callable, Protocol

Callback = Callable[[], None]

class CleanupService(Protocol):
    def add(self, cb: Callback) -> None: ...
    def run(self) -> None: ...
