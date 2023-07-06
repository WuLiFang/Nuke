# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

from glob import iglob

import os
import wulifang

from wulifang._util import cast_text
from wulifang.vendor.pyblish import api
from ._context_task import context_task


class CollectFXFootage(api.InstancePlugin):
    """从 CGTeamwork 获取特效素材."""

    order = api.CollectorOrder + 0.1
    label = "获取特效素材"
    families = ["CGTeamwork 任务"]

    def process(self, instance):
        # type: (api.Instance) -> None
        obj = instance
        ctx = obj.context
        entry = context_task(ctx)
        try:
            filebox = entry.filebox.get("fx")
        except ValueError:
            self.log.warn("找不到标识为 fx 的文件框，无法获取特效文件。可联系管理员进行设置")
            return
        wulifang.message.debug("fx filebox path: %s" % (filebox.path,))  # type: ignore
        try:
            match = cast_text(next(iglob(filebox.path + "/*")))  # type: ignore
            dir_ = os.path.dirname(match)
            ctx.create_instance("特效素材", folder=dir_, family="特效素材")
        except StopIteration:
            self.log.info("无特效素材")
