# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke
from wulifang.vendor.pyblish import api
from ._context_manifest import context_manifest
from wulifang._util import cast_str


class ValidateResolution(api.ContextPlugin):
    """检查分辨率是否匹配."""

    order = api.ValidatorOrder
    label = "检查分辨率"

    def process(self, context):
        # type: (api.Context) -> None
        ctx = context
        m = context_manifest(ctx)
        actual_width = int(nuke.numvalue(cast_str("root.width")))
        actual_height = int(nuke.numvalue(cast_str("root.height")))
        if not (m.shot.width and m.shot.height):
            self.log.warning("清单未指定分辨率")
            return
        expected_width = m.shot.width
        expected_height = m.shot.height
        if (expected_width, expected_height) != (
            actual_width,
            actual_height,
        ):
            raise ValueError(
                "分辨率和清单不一致: 应为=%dx%d，当前=%dx%d"
                % (
                    expected_width,
                    expected_height,
                    actual_width,
                    actual_height,
                ),
            )
