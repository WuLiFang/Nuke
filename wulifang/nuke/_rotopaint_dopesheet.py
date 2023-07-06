# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import re

import nuke
import nuke.rotopaint
import nuke.curvelib

from wulifang._util import cast_str, cast_text
from wulifang.nuke._util import (
    iter_deep_rotopaint_element,
    Panel as _Panel,
    CurrentViewer,
    raise_panel,
    RotopaintLifeTimeType,
    knob_of,
    RotoKnob,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from wulifang._compat.str import Str


def _rotopaint_keyframes(n):
    # type: (nuke.Node) -> ...
    key_frames = set([n.firstFrame(), n.lastFrame()])
    for i in iter_deep_rotopaint_element(knob_of(n, "curves", RotoKnob).rootLayer):
        if isinstance(
            i,
            (
                nuke.rotopaint.Shape,
                nuke.rotopaint.Stroke,
            ),
        ):
            attrs = i.getAttributes()
            lifetime_type = attrs.getValue(0, attrs.kLifeTimeTypeAttribute)
            if lifetime_type == RotopaintLifeTimeType.ALL:
                continue
            key_frames.add(int(attrs.getValue(0, attrs.kLifeTimeMAttribute)))
            key_frames.add(int(attrs.getValue(0, attrs.kLifeTimeNAttribute)))
    return sorted(key_frames)


def apply_timewarp(rotopaint, timewarp, all_stroke=False):
    # type: (nuke.Node, nuke.Node, bool) -> None
    """Apply timewarp to rotopaint node

    Args:
        rotopaint (nuke.Node): RotoPaint node
        timewarp (nuke.Node): TimeWarp node
        all_stroke (bool, optional): whether apply to invisible stroke.
            Defaults to False.
    """

    root_layer = knob_of(rotopaint, "curves", RotoKnob).rootLayer
    lookup = timewarp[cast_str("lookup")]
    time_map = {
        int(match[1]): int(match[0])
        for match in re.findall(
            r"x(\d+) (\d+)",
            cast_text(lookup.toScript()),
        )
    }

    def apply_lookup(attrs, key):
        # type: (nuke.curvelib.AnimAttributes, Str) -> None
        input_time = int(attrs.getValue(0, key))
        if input_time not in time_map:
            nuke.message(
                cast_str(
                    "在 {}.input 中找不到值为 {} 的关键帧".format(timewarp.name(), input_time)
                )
            )
            raise ValueError("timewarp lookup failed")
        output_time = time_map[int(input_time)]
        attrs.set(key, output_time)

    for i in iter_deep_rotopaint_element(root_layer):
        if isinstance(
            i,
            (
                nuke.rotopaint.Shape,
                nuke.rotopaint.Stroke,
            ),
        ):

            attrs = i.getAttributes()
            lifetime_type = attrs.getValue(0, attrs.kLifeTimeTypeAttribute)
            if lifetime_type == RotopaintLifeTimeType.ALL:
                continue

            if not all_stroke and not attrs.getValue(
                nuke.frame(), attrs.kVisibleAttribute
            ):
                continue
            apply_lookup(attrs, attrs.kLifeTimeNAttribute)
            apply_lookup(attrs, attrs.kLifeTimeMAttribute)


class Panel(_Panel):
    """Panel for rotopaint dopesheet command."""

    def __init__(
        self,
        rotopaint,  # type: nuke.Node
    ):
        # type: (...) -> None
        super(Panel, self).__init__(
            cast_str("RotoPaint摄影表"),
            cast_str("com.wlf-studio.rotopaint-dopesheet"),
        )
        if cast_text(rotopaint.Class()) != "RotoPaint":
            nuke.message(cast_str("请选中RotoPaint节点"))
            raise ValueError("require roto paint node")
        self.rotopaint = rotopaint

        n = nuke.createNode(cast_str("TimeWarp"))
        n.setInput(0, rotopaint)
        k = knob_of(n, "lookup", nuke.Array_Knob)
        k.fromScript(
            cast_str(
                "{curve L l %s}"
                % (
                    " ".join(
                        "x{} {}".format(i, i) for i in _rotopaint_keyframes(rotopaint)
                    ),
                )
            )
        )
        k.setExpression(cast_str("floor(curve)"))
        n.showControlPanel()
        CurrentViewer.show(n)
        self.timewarp = n

        rotopaint.hideControlPanel()
        k = nuke.Text_Knob(
            cast_str(""),
            cast_str("说明"),
            cast_str(
                "请在摄影表中编辑 %s.lookup 然后选择以下操作" % (cast_text(self.timewarp.name()),)
            ),
        )
        self.addKnob(k)
        k = nuke.Script_Knob(cast_str("apply"), cast_str("应用至可见笔画"))
        self.addKnob(k)
        k = nuke.Script_Knob(cast_str("apply_all"), cast_str("应用至所有笔画"))
        self.addKnob(k)
        k = nuke.Script_Knob(cast_str("cancel"), cast_str("Cancel"))
        self.addKnob(k)

    def show(self):
        super(Panel, self).show()
        raise_panel("DopeSheet.1")

    def knobChanged(self, knob):
        # type: (nuke.Knob) -> None
        is_finished = False
        if knob is self["apply"]:
            apply_timewarp(self.rotopaint, self.timewarp)
            is_finished = True
        elif knob is self["apply_all"]:
            apply_timewarp(self.rotopaint, self.timewarp, True)
            is_finished = True
        elif knob is self["cancel"]:
            is_finished = True

        if is_finished:
            nuke.delete(self.timewarp)
            self.rotopaint.showControlPanel()
            self.destroy()
            raise_panel("DAG.1")
