# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Iterable

from datetime import datetime

import wulifang.vendor.wulifang_manifest as m6t
from wulifang._util import TZ_CHINA, cast_text, shot_from_filename
from wulifang.vendor.pathlib2_unicode import Path
from wulifang.vendor.pyblish import api

from ._context_manifest import with_manifest
from ._context_user import context_user
import os


class Factory:
    def __init__(self, user):
        # type: (Text) -> None
        self.user = user

    def new(self):
        v = m6t.Manifest()
        v.created_at = datetime.now(TZ_CHINA)
        v.created_by = self.user
        return v


def _iter_manifest_paths(m):
    # type: (m6t.Manifest) -> Iterable[Text]
    yield m.path
    if m.base:
        for i in _iter_manifest_paths(m.base):
            yield i


class CollectManifest(api.InstancePlugin):
    """获取吾立方清单文件"""

    order = api.CollectorOrder + 0.01
    label = "获取吾立方清单"
    families = ["工作文件"]

    def process(self, instance):
        # type: (api.Instance) -> None
        obj = instance
        ctx = obj.context
        user = context_user(ctx)
        m = m6t.load(cast_text(Path(instance.name).parent), factory=Factory(user))
        for i in _iter_manifest_paths(m):
            self.log.info(i)
        if not m.shot.name:
            if m.shotMatcher:
                name, _ = os.path.splitext(obj.name)
                for matcher in m.shotMatcher:
                    if isinstance(matcher, m6t.shot_matcher.FilenameRegex):
                        match = matcher.match(name)
                        if match:
                            self.log.info("根据清单配置匹配为镜头: %s" % match)
                            m.shot.name = match
                            break
                else:
                    self.log.warning("当前文件格式不满足清单要求，无法获取镜头名称")
            else:
                m.shot.name = shot_from_filename(obj.name)

        with_manifest(ctx, m)
