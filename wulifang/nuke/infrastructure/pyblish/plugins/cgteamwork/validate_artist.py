# -*- coding=UTF-8 -*-
"""CGTeamWork pyblish plug-in.  """

from __future__ import absolute_import, division, print_function, unicode_literals
from wulifang.vendor.pyblish import api
from ._context_task import context_task
from .collect_user import NAME_KEY, ACCOUNT_ID_KEY
from wulifang._util import cast_text

class ValidateArtist(api.InstancePlugin):
    """检查任务是否在 CGTeamwork 上分配给当前用户。"""

    order = api.ValidatorOrder
    label = "检查制作者"
    families = ["CGTeamwork 用户"]

    def process(self, instance):
        obj = instance
        ctx = obj.context

        try:
            entry = context_task(ctx)
        except ValueError:
            self.log.info("无 CGTeamwork 任务")
            return

        current_id = cast_text(ctx.data[ACCOUNT_ID_KEY])
        current_artist = cast_text(ctx.data[NAME_KEY])
        expected_id_list = cast_text(entry["account_id"]).split(",")
        if current_id not in expected_id_list:
            raise ValueError(
                "用户不匹配: 应为='%s'， 当前='%s'" % (entry["artist"], current_artist)
            )
