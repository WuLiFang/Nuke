# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import annotations
from typing import Callable, Protocol, Text


Callback = Callable[[], None]
Cancel = Callable[[], None]


class CallbackService(Protocol):
    def on_render_start(self, cb: Callback, /) -> Cancel:
        ...

    def on_create(self, cb: Callback, /, *, node_class: Text = ...) -> Cancel:
        ...

    def on_drop_data(self, cb: Callback, /) -> Cancel:
        ...

    def on_user_create(self, cb: Callback, /) -> Cancel:
        ...

    def on_script_load(self, cb: Callback, /) -> Cancel:
        ...

    def on_script_save(self, cb: Callback, /) -> Cancel:
        ...

    def on_script_close(self, cb: Callback, /) -> Cancel:
        ...

    def on_ui_update(self, cb: Callback, /) -> Cancel:
        ...
