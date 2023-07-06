# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke
from wulifang.vendor.pyblish import api
from ._context_manifest import context_manifest
from wulifang._util import cast_str

class ValidateFPS(api.ContextPlugin):
    """检查帧速率是否匹配清单设置."""

    order = api.ValidatorOrder
    label = "检查帧速率"

    def process(self, context):
        # type: (api.Context) -> None
        ctx = context
        m = context_manifest(ctx)
        if not m.shot.fps:
            self.log.warning("清单未指定帧速率")
            return

        expected = m.shot.fps
        actual = nuke.numvalue(cast_str("root.fps"))
        if actual != expected:
            raise ValueError("帧速率和清单不一致: 应为=%s, 当前=%s" % (expected, actual))
