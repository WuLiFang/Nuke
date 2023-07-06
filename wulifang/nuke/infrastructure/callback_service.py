# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

import wulifang
from wulifang._util import cast_str, cast_text, cast_binary


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Callable
    from .. import _types
    from .._types.callback_service import Callback, Cancel, DropDataCallback
    from wulifang._compat.str import Str


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
            kwargs["nodeClass"] = cast_str(node_class)

        add(cb, **kwargs)

        def cancel():
            remove(cb, **kwargs)

        wulifang.cleanup.add(cancel)
        return cancel

    def on_will_render(self, cb, node_class=""):
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
        # type: (DropDataCallback) -> Cancel
        if not nuke.GUI:
            return lambda: None
        import nukescripts

        class local:
            is_cancelled = False

        def on_drop_data(mime_type, data):
            # type: (Str, Str) -> ...
            if local.is_cancelled:
                return
            return cb(cast_text(mime_type), cast_binary(data))

        def cancel():
            local.is_cancelled = True
            try:
                nukescripts.drop._gDropDataCallbacks.remove(on_drop_data)  # type: ignore
            except:
                pass

        nukescripts.addDropDataCallback(on_drop_data)

        wulifang.cleanup.add(cancel)
        return cancel

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
    # type: (CallbackService) -> _types.CallbackService
    return v
