# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional


import wulifang

import wulifang.vendor.cast_unknown as cast
import nuke
import wulifang.filename
from wulifang.nuke.infrastructure.recover_modifield_flag import recover_modifield_flag
from wulifang.vendor import cgtwq
from wulifang.vendor.pyblish import api
from ._context_task import context_task
from .._context_manifest import context_manifest
from wulifang.vendor.pathlib2_unicode import Path
import wulifang.nuke


class CollectAnimationVideo(api.InstancePlugin):
    """从 CGTeamwork 导入动画视频."""

    order = api.CollectorOrder + 0.1
    label = "导入动画文件"
    families = ["CGTeamwork 任务"]

    file_box_sign = "animation_videos"
    node_name = cast.binary("动画视频")

    def obtain_node(self, entry, shot, sign, node_name):
        # type: (cgtwq.Entry, Text, Text, bytes) -> Optional[nuke.Node]

        n = nuke.toNode(cast.binary(node_name))
        if n is None:
            try:
                dir_ = cast.text(entry.filebox.get(sign).path)  # type: ignore
            except ValueError:
                raise ValueError(
                    "找不到标识为 %s 的文件框，无法获取动画文件。可联系管理员进行设置" % (self.file_box_sign,)
                )
            videos = Path(dir_).glob("{}.*".format(shot))  # type: ignore
            for video in videos:  # type: ignore
                n = nuke.nodes.Read(name=cast.binary(node_name))  # type: ignore
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

    def process(self, instance):
        # type: (api.Instance) -> None
        obj = instance
        ctx = obj.context
        task = context_task(ctx)
        m = context_manifest(ctx)

        if not m.shot.name:
            self.log.warning("未配置镜头名")
            return
        with recover_modifield_flag():
            n = self.obtain_node(task, m.shot.name, self.file_box_sign, self.node_name)
            if not n:
                self.log.warning("找不到对应的动画视频文件")
