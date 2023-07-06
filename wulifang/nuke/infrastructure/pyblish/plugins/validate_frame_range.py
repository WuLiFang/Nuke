# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke
from wulifang.vendor.pyblish import api
from ._context_manifest import context_manifest
from wulifang._util import cast_str


class ValidateFrameRange(api.ContextPlugin):
    """检查帧范围是否匹配."""

    order = api.ValidatorOrder
    label = "检查帧范围"

    def process(self, context):
        # type: (api.Context) -> None
        ctx = context
        m = context_manifest(ctx)
        actual_first = int(nuke.numvalue(cast_str("root.first_frame")))
        actual_last = int(nuke.numvalue(cast_str("root.last_frame")))
        actual_count = actual_last - actual_first + 1
        if m.shot.frame_count < 1:
            self.log.info("清单未指定帧范围，自动设置为当前范围")
            m.shot.first_frame = actual_first
            m.shot.frame_count = actual_count
            return
        expected_first = m.shot.first_frame
        expected_frame = m.shot.frame_count
        if (expected_first, expected_frame) != (
            actual_first,
            actual_count,
        ):
            raise ValueError(
                "工程帧范围和清单不一致: 应为=%d-%d，当前=%d-%d"
                % (
                    expected_first,
                    expected_first + expected_frame - 1,
                    actual_first,
                    actual_first + actual_count - 1,
                ),
            )
