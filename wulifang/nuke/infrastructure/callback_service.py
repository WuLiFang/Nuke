# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Callable
    from .. import types
    from ..types.callback_service import Callback, Cancel


import nuke

import wulifang.nuke


class CallbackService:
    def _use(
        self,
        add,  # type: Callable[..., None]
        remove,  # type: Callable[..., None]
        cb,  # type: Callback
        node_class="",  # type: Text
    ):
        # type: (...) -> Cancel
        kwargs = {}
        if node_class:
            kwargs["nodeClass"] = node_class.encode("utf-8")

        add(cb, **kwargs)

        def cancel():
            remove(cb, **kwargs)

        wulifang.nuke.cleanup.add(cancel)
        return cancel

    def _use_add_only(
        self,
        add,  # type: Callable[..., None]
        cb,  # type: Callback
    ):
        # type: (...) -> Cancel
        class local:
            is_cancelled = False

        def handle():
            if local.is_cancelled:
                return
            cb()

        add(handle)

        def cancel():
            local.is_cancelled = True

        wulifang.nuke.cleanup.add(cancel)
        return cancel

    def on_render_start(self, cb, node_class=""):
        # type: (Callback, Text) -> Cancel
        return self._use(
            nuke.addBeforeRender,
            nuke.removeBeforeRender,
            cb,
            node_class,
        )

    def on_create(self, cb, node_class=""):
        # type: (Callback, Text) -> Cancel
        return self._use(
            nuke.addOnCreate,
            nuke.removeOnCreate,
            cb,
            node_class,
        )

    def on_drop_data(self, cb):
        # type: (Callback) -> Cancel
        if not nuke.GUI:
            return lambda: None
        import nukescripts

        return self._use_add_only(
            nukescripts.addDropDataCallback,
            cb,
        )

    def on_user_create(self, cb):
        # type: (Callback) -> Cancel
        return self._use(
            nuke.addOnUserCreate,
            nuke.removeOnUserCreate,
            cb,
        )

    def on_script_load(self, cb):
        # type: (Callback) -> Cancel
        return self._use(
            nuke.addOnScriptLoad,
            nuke.removeOnScriptLoad,
            cb,
        )

    def on_script_save(self, cb):
        # type: (Callback) -> Cancel
        return self._use(
            nuke.addOnScriptSave,
            nuke.removeOnScriptSave,
            cb,
        )

    def on_script_close(self, cb):
        # type: (Callback) -> Cancel
        return self._use(
            nuke.addOnScriptClose,
            nuke.removeOnScriptClose,
            cb,
        )

    def on_ui_update(self, cb):
        # type: (Callback) -> Cancel
        return self._use(
            nuke.addUpdateUI,
            nuke.removeUpdateUI,
            cb,
        )


def _(v):
    # type: (CallbackService) -> types.CallbackService
    return v
