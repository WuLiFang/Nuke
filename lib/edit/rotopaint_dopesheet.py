# -*- coding=UTF-8 -*-
"""Rotopaint dope sheet.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re

import nuke
import nuke.curveknob

import nuketools
from panels import PythonPanel
from rotopaint_tools import LIFETIME_TYPE_ALL, iter_layer


def _rotopaint_keyframes(n):
    key_frames = set([n.firstFrame(), n.lastFrame()])
    for i in iter_layer(n["curves"].rootLayer):
        if isinstance(i, nuke.curveknob.Layer):
            continue
        attrs = i.getAttributes()
        lifetime_type = attrs.getValue(0, attrs.kLifeTimeTypeAttribute)
        if lifetime_type == LIFETIME_TYPE_ALL:
            continue
        key_frames.add(int(attrs.getValue(0, attrs.kLifeTimeMAttribute)))
        key_frames.add(int(attrs.getValue(0, attrs.kLifeTimeNAttribute)))
    return sorted(key_frames)


def apply_timewarp(rotopaint, timewarp, all_stroke=False):
    """Apply timewarp to rotopaint node

    Args:
        rotopaint (nuke.Node): RotoPaint node
        timewarp (nuke.Node): TimeWarp node
        all_stroke (bool, optional): whether apply to invisible stroke.
            Defaults to False.
    """

    root_layer = rotopaint["curves"].rootLayer
    lookup = timewarp["lookup"]
    time_map = {
        int(match[1]): int(match[0])
        for match in re.findall(r"x(\d+) (\d+)", lookup.toScript())
    }

    def apply_lookup(attrs, key):
        input_time = int(attrs.getValue(0, key))
        if input_time not in time_map:
            nuke.message(
                "在 {}.input 中找不到值为 {} 的关键帧"
                .format(timewarp.name(), input_time)
                .encode("utf-8")
            )
            raise ValueError("timewarp lookup failed")
        output_time = time_map[int(input_time)]
        attrs.set(key, output_time)

    for i in iter_layer(root_layer):
        if isinstance(i, nuke.curveknob.Layer):
            continue
        attrs = i.getAttributes()
        lifetime_type = attrs.getValue(0, attrs.kLifeTimeTypeAttribute)
        if lifetime_type == LIFETIME_TYPE_ALL:
            continue

        if (not all_stroke and
                not attrs.getValue(nuke.frame(), attrs.kVisibleAttribute)):
            continue
        apply_lookup(attrs, attrs.kLifeTimeNAttribute)
        apply_lookup(attrs, attrs.kLifeTimeMAttribute)


class Panel(PythonPanel):
    """Panel for rotopaint dopesheet command.  """
    widget_id = b'com.wlf.rotopaint_dopesheet'

    def __init__(self, rotopaint):
        super(Panel, self).__init__(
            'RotoPaint摄影表'.encode("utf-8"), self.widget_id)
        if rotopaint.Class() != "RotoPaint":
            nuke.message("请选中RotoPaint节点".encode("utf-8"))
            raise ValueError("require roto paint node")
        self.rotopaint = rotopaint
        self.timewarp = nuke.nodes.TimeWarp(
            inputs=[rotopaint],
            lookup='{{ curve L l {}}}'.format(
                ' '.join('x{} {}'.format(i, i)
                         for i in _rotopaint_keyframes(rotopaint))
            ),
        )
        _ = self.timewarp[b"lookup"].setExpression(b"floor(curve)")
        self.timewarp.showControlPanel()
        viewer = nuke.activeViewer()
        _ = viewer.node().setInput(viewer.activeInput() or 0, self.timewarp)

        k = nuke.Text_Knob(
            b"",
            "说明".encode("utf-8"),
            ("请在摄影表中编辑 {} 然后选择以下操作"
             .format(self.timewarp.name())
             .encode("utf-8")))
        self.addKnob(k)
        k = nuke.Script_Knob(b"apply", "应用至可见笔画".encode("utf-8"))
        self.addKnob(k)
        k = nuke.Script_Knob(b"apply_all", "应用至所有笔画".encode("utf-8"))
        self.addKnob(k)
        k = nuke.Script_Knob(b'cancel', 'Cancel'.encode("utf-8"))
        self.addKnob(k)

    def show(self):
        super(Panel, self).show()
        nuketools.raise_panel("DopeSheet.1")

    def knobChanged(self, knob):
        """Override. """
        is_finished = False
        if knob is self['apply']:
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
            nuketools.raise_panel("DAG.1")
