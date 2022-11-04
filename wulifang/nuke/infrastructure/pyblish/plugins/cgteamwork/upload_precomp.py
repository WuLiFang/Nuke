# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False


import nuke
import wulifang.vendor.cast_unknown as cast
from wulifang.vendor.pyblish import api

from .._copy_file import copy_file
from ._context_work_file_dir import context_work_file_dir


class UploadPrecomp(api.InstancePlugin):
    """上传相关预合成文件至CGTeamWork."""

    order = api.IntegratorOrder
    label = "上传预合成文件"
    families = ["CGTeamwork 任务"]

    def process(self, instance):
        # type: (api.Instance) -> None
        nodes = nuke.allNodes(b"Precomp")
        if not nodes:
            return
        ctx = instance.context
        dest = context_work_file_dir(ctx)
        for n in nuke.allNodes(b"Precomp"):
            src = cast.text(nuke.filename(n))
            if src.startswith(dest.replace("\\", "/")):
                continue
            n["file"].setValue(copy_file(src, dest))  # type: ignore
        _ = nuke.scriptSave()
