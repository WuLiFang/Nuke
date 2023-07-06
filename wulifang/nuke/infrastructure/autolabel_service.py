# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional, Iterator, TypeVar, Set

    from .. import _types
    import wulifang._types
    from wulifang._compat.str import Str

    T = TypeVar("T")

import nuke
from autolabel import autolabel

from wulifang._util import is_local_file, cast_text, cast_str
import wulifang.vendor.six as six


def _parse_layer(s):
    # type: (Text) -> ...
    layer, channel = s.split(".", 2)

    return layer, channel


def _uniq(s):
    # type: (Iterator[T]) -> Iterator[T]
    m = set()  # type: Set[T]
    for i in s:
        if i not in m:
            yield i
            m.add(i)


class _Shuffle2Mapping:
    def __init__(
        self,
        in_channel,
        in_layer_index,
        in_channel_index,
        out_channel,
        out_layer_index,
        out_channel_index,
    ):
        # type: (Text, int, int, Text,int,int) -> None
        self.in_channel = in_channel
        self.in_layer_index = in_layer_index
        self.in_channel_index = in_channel_index
        self.out_channel = out_channel
        self.out_layer_index = out_layer_index
        self.out_channel_index = out_channel_index

    @classmethod
    def parse(cls, s):
        # type: (Text) -> Iterator[_Shuffle2Mapping]
        parts = s.split(" ")
        for end_index in six.moves.range(1 + 6, len(parts) + 1, 6):
            start_index = end_index - 6
            yield cls(
                parts[start_index],
                int(parts[start_index + 1]),
                int(parts[start_index + 2]),
                parts[start_index + 3],
                int(parts[start_index + 4]),
                int(parts[start_index + 5]),
            )

    def in_layer(self):
        return _parse_layer(self.in_channel)[0]

    def out_layer(self):
        return _parse_layer(self.out_channel)[0]


class AutolabelService:
    def __init__(self, file):
        # type: (wulifang._types.FileService) -> None
        self.file = file

    def _with_next(self, text, center=False):
        # type: (Text, bool) -> Str

        if not text:
            return autolabel()

        ret = cast_text(autolabel()).split("\n")
        ret.insert(1, cast_text(text))
        ret = "\n".join(ret).rstrip("\n")
        if center:
            ret = (
                '<div align="center" ' 'style="margin:0px;padding:0px">{}</div>'
            ).format(ret)
        return cast_str(ret)

    def _keyer(self):
        label = "输入通道 : " + cast_text(nuke.value(cast_str("this.input")))
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

        if is_local_file(cast_text(nuke.filename(this))):
            missing_frames = list(
                self.file.missing_frames(
                    cast_text(nuke.filename(this)),
                    this.firstFrame(),
                    this.lastFrame(),
                )
            )
            if missing_frames:
                label += "\n<span>缺帧: {}</span>".format(
                    nuke.FrameRanges(missing_frames),
                )

        label += "\n<b>修改日期: </b>{}".format(this.metadata(cast_str("input/mtime")))
        ret = self._with_next(label, True)
        return ret

    def _shuffle(self):
        channels = dict.fromkeys(["in", "in2", "out", "out2"], "")
        for i in channels.keys():
            channel_value = cast_text(nuke.value(cast_str("this." + i)))
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

    def _shuffle2(self):
        mapping_text = cast_text(nuke.value(cast_str("this.mappings"), cast_str("")))[1:-1]
        l = list(_Shuffle2Mapping.parse(mapping_text))

        l_channel_changed = [i for i in l if i.in_channel_index != i.out_channel_index]
        l_channel_changed = sorted(
            [
                i
                for i in l
                if any(
                    j.out_layer_index == i.out_layer_index for j in l_channel_changed
                )
            ],
            key=lambda x: (x.out_layer_index, x.out_channel_index),
        )
        l_channel_unchanged = [
            i
            for i in l
            if all(j.out_layer_index != i.out_layer_index for j in l_channel_changed)
        ]

        label = ""
        label += "".join(
            _uniq(
                "%s -> %s\n" % (i.in_layer(), i.out_layer())
                for i in l_channel_unchanged
            )
        )
        label += "".join(
            "%s -> %s\n" % (i.in_channel, i.out_channel) for i in l_channel_changed
        )

        ret = self._with_next(label)
        return ret

    def _time_offset(self):
        this = nuke.thisNode()
        return self._with_next("{:.0f}".format(this[cast_str("time_offset")].value()))

    def autolabel(self):
        # type: () -> Optional[Str]

        this = nuke.thisNode()
        class_ = cast_text(this.Class())
        dict_ = {
            "Keyer": self._keyer,
            "Read": self._read,
            "Shuffle": self._shuffle,
            "Shuffle2": self._shuffle2,
            "TimeOffset": self._time_offset,
        }

        if class_ in dict_:
            return dict_[class_]()


def _(v):
    # type: (AutolabelService) -> _types.AutolabelService
    return v
