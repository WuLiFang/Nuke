# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang._util import cast_str, cast_text, iteritems
from wulifang.nuke._util import (
    Panel,
    CurrentViewer,
    undoable,
    create_copy_nodes,
    replace_node,
    is_node_deleted,
    knob_of,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


class RenameChannels(Panel):
    """Dialog UI of channel_rename."""

    def __init__(
        self,
        node,  # type: nuke.Node
    ):
        def order(
            name,  # type: Text
        ):
            return (
                not name.startswith("rgba."),
                name.split(".")[0],
                name.endswith(".alpha"),
                name.endswith(".blue"),
                name.endswith(".green"),
                name.endswith(".red"),
            )

        def colorize(text):
            # type: (Text) -> Text
            ret = text
            repl = {
                ".red": '.<span style="color:#FF4444">red</span>',
                ".green": '.<span style="color:#44FF44">green</span>',
                ".blue": '.<span style="color:#4444FF">blue</span>',
            }
            for k, v in iteritems(repl):
                ret = ret.replace(k, v)
            return ret

        super(RenameChannels, self).__init__(
            cast_str("重命名通道"),
            cast_str("com.wlf-studio.rename-channels"),
        )

        viewer = CurrentViewer()
        viewer.record()
        n = node
        self._channels = sorted(
            (cast_text(channel) for channel in n.channels()),
            key=order,
        )
        self._node = n
        self._viewer = viewer

        nuke.Undo.disable()

        n = nuke.nodes.LayerContactSheet(inputs=[n], showLayerNames=1)
        self._layer_contact_sheet = n

        viewer.show(n)
        knob_of(
            viewer.obtain().node(),
            "channels",
            nuke.Channel_Knob,
        ).setValue(cast_str("rgba"))

        last_layer = ""
        for channel in self._channels:
            layer = channel.split(".")[0]
            if last_layer and layer != last_layer:
                self.addKnob(nuke.Text_Knob(cast_str("")))
            self.addKnob(
                nuke.String_Knob(
                    cast_str(channel),
                    cast_str(colorize(channel)),
                )
            )
            last_layer = layer
        self.addKnob(nuke.Text_Knob(cast_str("")))
        k = nuke.Script_Knob(cast_str("ok"), cast_str("OK"))
        k.setFlag(nuke.STARTLINE)
        self.addKnob(k)
        k = nuke.Script_Knob(cast_str("cancel"), cast_str("Cancel"))
        self.addKnob(k)

        nuke.Undo.enable()

        self.add_callbacks()

    def add_callbacks(self):
        """Add nuke callbacks."""

        nuke.addOnDestroy(RenameChannels.destroy, args=(self,))
        nuke.addOnUserCreate(RenameChannels.destroy, args=(self,))

    def remove_callbacks(self):
        """Remove nuke callbacks."""

        nuke.removeOnDestroy(RenameChannels.destroy, args=(self,))
        nuke.removeOnUserCreate(RenameChannels.destroy, args=(self,))

    def destroy(self):
        """Destroy the panel."""

        if not is_node_deleted(self._layer_contact_sheet):
            nuke.Undo.disable()
            knob_of(
                self._layer_contact_sheet,
                "label",
                nuke.String_Knob,
            ).setValue(cast_str("[delete this]"))
            nuke.Undo.enable()
        self.remove_callbacks()
        super(RenameChannels, self).destroy()

    def knobChanged(self, knob):
        # type: (nuke.Knob) -> None

        if knob in (self["ok"], self["cancel"]):
            self._viewer.recover()
            if knob is self["ok"]:
                self.accept()
            else:
                self.reject()
            self.destroy()

    @undoable("重命名通道")
    def accept(self):
        """Execute named copy."""

        n = create_copy_nodes(
            self._node,
            {channel: cast_text(self[channel].value()) for channel in self._channels},
        )
        replace_node(self._node, n)
