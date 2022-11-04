# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals
from datetime import datetime


from wulifang.vendor.pyblish import api
from ._context_manifest import context_manifest
import wulifang.vendor.wulifang_manifest as m6t
from wulifang._util import TZ_CHINA
from ._context_user import context_user


class SaveManifest(api.InstancePlugin):
    """上传工作文件至CGTeamWork."""

    order = api.ExtractorOrder
    label = "保存清单文件"
    families = ["工作文件"]

    def process(self, instance):
        # type: (api.Instance) -> None
        obj = instance
        ctx = obj.context
        m = context_manifest(ctx)
        m.last_modified_by = context_user(ctx)
        m.last_modified_at = datetime.now(TZ_CHINA)
        assert m.path, "missing manifest path"
        m6t.save(m)
