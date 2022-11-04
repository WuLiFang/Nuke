# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import List, Text


import wulifang.vendor.cast_unknown as cast
import nuke

from wulifang.vendor import cgtwq
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
        entry = context_task(ctx)

        if entry["leader_status"] == "Check":
            self.log.info("任务已经是检查状态, 无需提交。")
            return

        note = nuke.getInput(
            "CGTeamWork任务提交备注(Cancel则不提交)".encode("utf-8"),
            b"",
        )

        if note is None:
            self.log.info("用户选择不提交任务。")
            return
        note = cast.text(note)

        message = cgtwq.Message(note)
        filenames = []  # type: List[Text]
        submit_image = obj.data.get(IMAGE_KEY)
        if submit_image:
            filenames.append(cast.text(submit_image.path))
            message.images.append(submit_image)  # type: ignore

        if not filenames:
            self.log.warning("缺少可提交的文件")
            return
        entry.flow.submit(filenames=tuple(filenames), message=message)
