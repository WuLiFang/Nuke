# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import List, Text

import nuke

from wulifang._util import cast_text, cast_str
from wulifang.vendor.cgtwq import MessageV2
from wulifang.vendor.pyblish import api
from ._context_task import context_task
from .upload_image import IMAGE_KEY


class Submit(api.InstancePlugin):
    """在CGTeamWork上提交任务."""

    order = api.IntegratorOrder + 0.2
    label = "提交任务"
    families = ["CGTeamwork 任务"]

    def process(self, instance):
        # type: (api.Instance) -> None
        obj = instance
        ctx = obj.context
        task = context_task(ctx)
        for (status,) in task.table().rows("task.status"):
            if status == "Check":
                self.log.info("任务已经是检查状态, 无需提交。")
                return

        note = nuke.getInput(
            cast_str("CGTeamWork任务提交备注(Cancel则不提交)"),
            cast_str(""),
        )

        if note is None:
            self.log.info("用户选择不提交任务。")
            return
        note = cast_text(note)

        message = MessageV2(note)
        filenames = []  # type: List[Text]
        image_data = obj.data.get(IMAGE_KEY)
        if image_data:
            image, path = image_data
            filenames.append(cast_text(path))
            message.images = (image,)

        if not filenames:
            self.log.warning("缺少可提交的文件")
            return
        task.client.flow.submit(
            task.id,
            filenames,
            message,
        )
