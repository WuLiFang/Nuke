# -*- coding=UTF-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional

from wulifang.vendor import cgtwq
import nuke
import wulifang.nuke
from wulifang.vendor.pathlib2_unicode import Path

import wulifang.vendor.cast_unknown as cast


def import_task_video(entry, shot, sign):
    # type: (cgtwq.Entry, Text, Text) -> Optional[nuke.Node]
    """Import corresponse video by filebox sign.

    Args:
        sign (unicode): Server defined fileboxsign

    Returns:
        Optional[nuke.Node]: Created read node.
    """

    node_name = {"animation_videos": "动画视频"}.get(sign, sign)
    n = nuke.toNode(cast.binary(node_name))
    if n is None:
        dir_ = entry.filebox.get(sign).path  # type: Text
        videos = Path(dir_).glob("{}.*".format(shot))
        for video in videos:
            n = nuke.nodes.Read(name=cast.binary(node_name))
            k = n[b"file"]
            assert isinstance(k, nuke.File_Knob), k
            k.fromUserText(cast.binary(video))
            break
    if not n:
        return
    _ = n[b"frame_mode"].setValue(b"start_at")
    _ = n[b"frame"].setValue(
        cast.binary("{:.0f}".format(nuke.numvalue(b"root.first_frame"))),
    )
    wulifang.nuke.active_viewer.set_default_input(n, 4)
    return n
