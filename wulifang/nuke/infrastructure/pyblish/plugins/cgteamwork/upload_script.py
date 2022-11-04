# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

from wulifang.vendor.pyblish import api

from .._copy_file import copy_file
from ._context_work_file_dir import context_work_file_dir


class UploadScript(api.InstancePlugin):
    """上传工作文件至CGTeamWork."""

    order = api.IntegratorOrder + 0.1
    label = "上传工作文件"
    families = ["CGTeamwork 任务"]

    def process(self, instance):
        # type: (api.Instance) -> None
        obj = instance
        ctx = obj.context
        dest = context_work_file_dir(ctx)
        _ = copy_file(obj.data["work_file"].name, dest)
