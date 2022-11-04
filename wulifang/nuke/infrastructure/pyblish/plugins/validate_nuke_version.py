# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke
from wulifang.vendor.pyblish import api
from ._context_manifest import context_manifest


class ValidateNukeVersion(api.ContextPlugin):
    """检查 Nuke 版本是否匹配。"""

    order = api.ValidatorOrder
    label = "检查 Nuke 版本"

    def process(self, context):
        # type: (api.Context) -> None
        ctx = context
        m = context_manifest(ctx)
        m2 = m.software.nuke
        major, minor, release = (
            nuke.NUKE_VERSION_MAJOR,
            nuke.NUKE_VERSION_MINOR,
            nuke.NUKE_VERSION_RELEASE,
        )
        if not m2.major:
            self.log.info("清单中未指定 Nuke 版本，自动设置为当前版本")
            m2.major = major
            m2.minor = minor
            m2.release = release
            return
        if m2.release:
            actual_version = "%d.%dv%d" % (major, minor, release)
            expected_version = "%d.%dv%d" % (m2.major, m2.minor, m2.release)
        elif m2.minor:
            actual_version = "%d.%d" % (major, minor)
            expected_version = "%d.%d" % (m2.major, m2.minor)
        else:
            actual_version = "%d" % (major,)
            expected_version = "%d" % (m2.major,)
        if expected_version != actual_version:
            raise ValueError(
                "Nuke 版本和清单不一致: 应为=%s, 当前=%s"
                % (
                    expected_version,
                    actual_version,
                ),
            )
