# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional

    from .. import types
    import wulifang.types


import nuke
from autolabel import autolabel

import wulifang.vendor.cast_unknown as cast


class AutolabelService:
    def __init__(self, file):
        # type: (wulifang.types.FileService) -> None
        self.file = file

    def _with_next(self, text, center=False):
        # type: (Text, bool) -> bytes

        ret = cast.text(autolabel()).split("\n")
        ret.insert(1, cast.text(text))
        ret = "\n".join(ret).rstrip("\n")
        if center:
            ret = (
                '<div align="center" ' 'style="margin:0px;padding:0px">{}</div>'
            ).format(ret)
        return cast.binary(ret)

    def _keyer(self):
        label = "输入通道 : " + cast.text(nuke.value(b"this.input"))
        ret = self._with_next(label)
        return ret

    def _read(self):
        this = nuke.thisNode()
        label = (
            "<style>* {font-family:微软雅黑} " "span {color:red} b {color:#548DD4}</style>"
        )
        label += "<b>帧范围: </b><span>{} - {}</span>".format(
            this.firstFrame(), this.lastFrame()
        )
        missing_frames = list(
            self.file.missing_frames(
                cast.text(nuke.filename(this)),
                this.firstFrame(),
                this.lastFrame(),
            )
        )
        if missing_frames:
            label += "\n<span>缺帧: {}</span>".format(
                nuke.FrameRanges(missing_frames),
            )
        label += "\n<b>修改日期: </b>{}".format(this.metadata(b"input/mtime"))
        ret = self._with_next(label, True)
        return ret

    def _shuffle(self):
        channels = dict.fromkeys(["in", "in2", "out", "out2"], "")
        for i in channels.keys():
            channel_value = cast.text(nuke.value(cast.binary("this." + i)))
            if channel_value != "none":
                channels[i] = channel_value + " "
        label = (
            channels["in"]
            + channels["in2"]
            + "-> "
            + channels["out"]
            + channels["out2"]
        ).rstrip(" ")
        ret = self._with_next(label)
        return ret

    def _time_offset(self):
        this = nuke.thisNode()
        return self._with_next("{:.0f}".format(this[b"time_offset"].value()))

    def autolabel(self):
        # type: () -> Optional[bytes]

        this = nuke.thisNode()
        class_ = this.Class()
        dict_ = {
            b"Keyer": self._keyer,
            b"Read": self._read,
            b"Shuffle": self._shuffle,
            b"TimeOffset": self._time_offset,
        }

        if class_ in dict_:
            return dict_[class_]()


def _(v):
    # type: (AutolabelService) -> types.AutolabelService
    return v
