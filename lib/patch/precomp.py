# -*- coding=UTF-8 -*-
"""Patch nukescript precomp functions.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import nuke

from pathlib2_unicode import PurePath
import cast_unknown as cast

from .core import BasePatch

LOGGER = logging.getLogger(__name__)


class PatchPrecompDialog(BasePatch):
    """Enhance precomp creation"""

    target = "nukescripts.PrecompOptionsDialog.__init__"

    @classmethod
    def func(cls, *args, **kwargs):
        self = args[0]
        cls.orig(*args, **kwargs)

        self.precompName = nuke.String_Knob(
            "precomp_name".encode("utf-8"),
            "预合成名称".encode("utf-8"),
            "precomp1".encode("utf-8"),
        )
        self.addKnob(self.precompName)

        self.scriptPath.setLabel("脚本路径".encode("utf-8"))
        self.renderPath.setLabel("渲染路径".encode("utf-8"))
        self.channels.setLabel("输出通道".encode("utf-8"))
        self.origNodes.setLabel("原节点".encode("utf-8"))

        _knob_changed(self, self.precompName)
        nuke.addKnobChanged(
            lambda self: _knob_changed(self, nuke.thisKnob()),
            args=self,
            nodeClass=b"PanelNode",
            node=self._PythonPanel__node,
        )  # pylint: disable=protected-access


def _on_precomp_name_changed(self, knob):
    rootpath = PurePath(cast.text(nuke.value(b"root.name")))
    name = cast.text(knob.value()) or "precomp1"
    script_path = (
        rootpath.parent
        / "".join([rootpath.stem] + [".{}".format(name)] + rootpath.suffixes)
    ).as_posix()
    render_path = "precomp/{0}/{0}.%04d.exr".format(
        "".join(
            [rootpath.stem]
            + [".{}".format(name)]
            + [i for i in rootpath.suffixes if i != ".nk"]
        )
    )
    self.scriptPath.setValue(script_path.encode("utf-8"))
    self.renderPath.setValue(render_path.encode("utf-8"))


def _knob_changed(self, knob):
    {self.precompName: _on_precomp_name_changed,}.get(
        knob, lambda *_: None
    )(self, knob)


def enable():
    """Enable patch."""

    PatchPrecompDialog.enable()


def disable():
    """Disable patch."""

    PatchPrecompDialog.disable()
