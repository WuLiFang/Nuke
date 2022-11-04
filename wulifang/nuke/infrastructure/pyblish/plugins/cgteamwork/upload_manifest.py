# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

from wulifang.vendor.pyblish import api

from .._copy_file import copy_file
from .._context_manifest import context_manifest

from ._context_work_file_dir import context_work_file_dir


class UploadManifest(api.InstancePlugin):
    """上传清单文件至 CGTeamWork。"""

    order = api.IntegratorOrder + 0.1
    label = "上传清单文件"
    families = ["CGTeamwork 任务"]

    def process(self, instance):
        # type: (api.Instance) -> None
        obj = instance
        ctx = obj.context
        m = context_manifest(ctx)
        dest = context_work_file_dir(ctx)
        copy_file(m.path, dest)
