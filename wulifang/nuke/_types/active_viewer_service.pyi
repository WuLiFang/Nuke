# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import annotations

from typing import Protocol
import nuke

class ActiveViewerService(Protocol):
    def set_input(self, node: nuke.Node, index: int = ..., /) -> None: ...
    def set_default_input(self, node: nuke.Node, index: int = ..., /) -> None: ...

    # def recover_input(self) -> ContextManager[None]: ...
