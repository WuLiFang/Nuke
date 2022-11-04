# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import annotations

from typing import Protocol
import wulifang.vendor.wulifang_manifest as m6t

class ManifestService(Protocol):
    def request_user_edit(
        self,
        manifest: m6t.Manifest,
        /,
        *,
        wait: bool = ...,
    ) -> None: ...
