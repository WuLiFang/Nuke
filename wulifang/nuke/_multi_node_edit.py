# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang._util import cast_str, cast_text
from wulifang.nuke._util import (
    Panel,
    copy_knob_flags,
    Progress,
    undoable,
    try_apply_knob_values,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterable, Any, Text


def _select_by_class(
    nodes,  # type: list[nuke.Node]
):
    # type: (...) -> list[nuke.Node]

    class_names = sorted(
        set(n.Class() for n in nodes),
        key=cast_text,
    )
    if len(class_names) > 1:
        choice = nuke.choice(
            cast_str("选择节点分类"), cast_str("节点分类"), class_names, default=0
        )
        if choice is not None:
            nodes = [n for n in nodes if n.Class() == class_names[choice]]
        else:
            nodes = [n for n in nodes if n.Class() == nodes[0].Class()]
    return nodes


class MultiNodeEdit(Panel):
    def __init__(
        self,
        nodes,  # type: Iterable[nuke.Node]
    ):
        super(MultiNodeEdit, self).__init__(
            cast_str("同时编辑多个节点"),
            cast_str("com.wlf-studio.multi-node-edit"),
        )

        nodes = list(nodes)
        nodes = _select_by_class(nodes)
        self.nodes = nodes
        self._changes = {}  # type: dict[Text, Any]

        knobs = nodes[0].allKnobs()

        self.addKnob(
            nuke.Text_Knob(cast_str("以 %s 为模版" % (cast_text(nodes[0].name()),)))
        )
        self.addKnob(nuke.Tab_Knob(cast_str(""), nodes[0].Class()))

        for k_raw in knobs:
            name = k_raw.name()
            label = cast_text(k_raw.label())
            # None has different effect when creating new knob
            label_input = cast_str(label) or None
            if (
                isinstance(k_raw, (nuke.Script_Knob, nuke.Obsolete_Knob))
                or type(k_raw) is nuke.Knob
            ):
                continue
            elif isinstance(k_raw, nuke.Channel_Knob):
                k = nuke.Channel_Knob(name, label_input, k_raw.depth())
            elif isinstance(k_raw, nuke.Enumeration_Knob):
                k = nuke.Enumeration_Knob(name, label_input, k_raw.values())
            elif isinstance(k_raw, nuke.Array_Knob):
                k = nuke.Array_Knob(name, label_input)
                k.setRange(k_raw.min(), k_raw.max())
            else:
                try:
                    k = type(k_raw)(name, label_input)
                except:
                    # not supported
                    continue
            copy_knob_flags(k, k_raw)
            try:
                k.setValue(k_raw.value())  # type: ignore
            except TypeError:
                pass

            self.addKnob(k)

        self.addKnob(nuke.EndTabGroup_Knob(cast_str("")))

        self._rename_knob = nuke.EvalString_Knob(
            cast_str(""),
            cast_str("重命名"),
        )
        self.addKnob(self._rename_knob)
        self.addKnob(
            nuke.ColorChip_Knob(
                cast_str("tile_color"),
                cast_str("节点颜色"),
            )
        )
        self.addKnob(
            nuke.ColorChip_Knob(
                cast_str("gl_color"),
                cast_str("框线颜色"),
            )
        )
        k = nuke.PyScript_Knob(
            cast_str("ok"),
            cast_str("OK"),
        )
        k.setFlag(nuke.STARTLINE)
        self.addKnob(k)
        self.addKnob(
            nuke.PyScript_Knob(
                cast_str("cancel"),
                cast_str("Cancel"),
                cast_str("nuke.tabClose()"),
            )
        )

    def knobChanged(self, knob):
        # type: (nuke.Knob) -> None
        if knob is self["ok"]:
            try:
                self.execute()
                self.destroy()
            except Progress.Cancelled:
                pass
        else:
            self._changes[cast_text(knob.name())] = knob.value()

    @undoable("同时编辑多个节点")
    def execute(self):
        with Progress("应用变更") as p:
            for index, n in enumerate(self.nodes):
                p.set_value(float(index) / len(self.nodes))
                p.set_message(cast_text(n.fullName()))
                try_apply_knob_values(n, self._changes)
                name = self._rename_knob.evaluate()
                if name:
                    try:
                        n.setName(name)
                    except ValueError:
                        pass
