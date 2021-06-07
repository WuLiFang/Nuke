# -*- coding=UTF-8 -*-
"""Node auto label.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import nuke
import six
from autolabel import autolabel

import asset
import asset.missing_frames
import cast_unknown as cast

LOGGER = logging.getLogger(__name__)


def custom_autolabel():
    """
    add addition information on Node in Gui
    """

    def _add_to_autolabel(text, center=False):

        if not isinstance(text, (six.binary_type, six.text_type)):
            return
        ret = cast.text(autolabel()).split("\n")
        ret.insert(1, cast.text(text))
        ret = "\n".join(ret).rstrip("\n")
        if center:
            ret = (
                '<div align="center" ' 'style="margin:0px;padding:0px">{}</div>'
            ).format(ret)
        return ret

    def _keyer():
        label = "输入通道 : " + cast.text(nuke.value(b"this.input"))
        ret = _add_to_autolabel(label)
        return ret

    def _read():
        label = (
            "<style>* {font-family:微软雅黑} " "span {color:red} b {color:#548DD4}</style>"
        )
        label += "<b>帧范围: </b><span>{} - {}</span>".format(
            this.firstFrame(), this.lastFrame()
        )
        missing_frames = asset.missing_frames.get(
            cast.text(nuke.filename(this)),
            this.firstFrame(),
            this.lastFrame(),
        )
        if missing_frames:
            label += "\n<span>缺帧: {}</span>".format(
                nuke.FrameRanges(missing_frames),
            )
        label += "\n<b>修改日期: </b>{}".format(this.metadata(b"input/mtime"))
        ret = _add_to_autolabel(label, True)
        return ret

    def _shuffle():
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
        ret = _add_to_autolabel(label)
        return ret

    def _timeoffset():
        return _add_to_autolabel("{:.0f}".format(this[b"time_offset"].value()))

    this = nuke.thisNode()
    class_ = this.Class()
    dict_ = {
        b"Keyer": _keyer,
        b"Read": _read,
        b"Shuffle": _shuffle,
        b"TimeOffset": _timeoffset,
    }

    if class_ in dict_:
        ret = dict_[class_]()
        if ret is None:
            return None
        return cast.binary(ret)


def add_autolabel():
    """Add custom autolabel."""

    LOGGER.info("增强节点标签")
    nuke.addAutolabel(custom_autolabel)
