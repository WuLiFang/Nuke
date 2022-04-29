# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Protocol

class PublishService(Protocol):
    def validate(self) -> None: ...
    def request_validate(self) -> None: ...
    def publish(self) -> None: ...
