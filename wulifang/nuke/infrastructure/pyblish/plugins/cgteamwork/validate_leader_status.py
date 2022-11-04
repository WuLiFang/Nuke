# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


from wulifang.vendor.pyblish import api
from ._context_task import context_task


class ValidateLeaderStatus(api.InstancePlugin):
    """检查任务是否允许提交。"""

    order = api.ValidatorOrder
    label = "检查组长状态"
    families = ["CGTeamwork 任务"]

    def process(self, instance):
        # type: (api.Instance) -> None
        entry = context_task(instance.context)

        status = entry["leader_status"]
        if status in ("Approve", "Close"):
            raise ValueError("任务状态为 %s，禁止提交" % status)
