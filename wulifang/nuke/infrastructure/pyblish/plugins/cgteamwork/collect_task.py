# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import wulifang


from wulifang.vendor.pyblish import api
from .._context_manifest import context_manifest
from ._context_task import with_task
import wulifang.vendor.cgtwq as cgtwq
from wulifang.vendor.cgtwq.helper.wlf import get_database_by_file, DatabaseError
from wulifang._util import cast_text


class CollectTask(api.InstancePlugin):
    """获取工作文件对应的 CGTeamWork任务。"""

    order = api.CollectorOrder + 0.05
    label = "获取 CGTeamwork 任务"
    families = ["工作文件"]
    default_segment_name = "合成"

    def process(self, instance):
        # type: (api.Instance) -> None
        obj = instance
        filename = obj.name
        ctx = instance.context
        m = context_manifest(obj)
        m2 = m.cgteamwork
        if not m2.database:
            if m.project.name:
                name = m.project.name
                match = cgtwq.PROJECT.filter(
                    (cgtwq.Field("full_name") == name) | (cgtwq.Field("entity") == name)
                )["database"]
                if len(match) == 1:
                    m2.database = match[0]
                elif len(match) > 1:
                    self.log.info("有多个项目匹配名称 '%s'" % (name,))
                else:
                    self.log.info("无法通过项目名称 '%s' 匹配项目" % (name,))
        if not m2.database:
            try:
                m2.database = get_database_by_file(filename)
            except DatabaseError:
                self.log.info("无法通过文件名匹配项目")
        if not m2.database:
            wulifang.manifest.request_user_edit(m, wait=True)
        if not m2.database:
            self.log.info("清单未指定 CGTeamwork 数据库")
            return
        if not m2.module:
            m2.module = "shot"

        database = cgtwq.Database(m2.database)
        if not m.shot.fps:
            try:
                m.shot.fps = float(database.metadata["fps"])
                self.log.info("从 CGTeamwork 数据库获取了帧速率")
            except:
                pass

        if not m.project.name:
            project = cgtwq.PROJECT.filter(
                cgtwq.Field("database") == m2.database
            ).to_entry()
            m.project.name = project["full_name"]
            self.log.info("自动设置清单项目名称为 %s" % m.project.name)
        module = database.module(m2.module)
        entry = None
        if not m2.pipeline.id:
            if m2.task.id:
                entry = module.select(m2.task.id).to_entry()
                m2.pipeline.id = cast_text(entry.get_fields("pipeline.id")[0])
            else:
                name = m.project.segment.name or self.default_segment_name
                match = database.pipeline.filter(
                    (cgtwq.Field("module") == m2.module)
                    & (cgtwq.Field("entity") == name)
                )
                self.log.info("清单未配置流程，自动从 '%s' 查找名为 '%s' 的流程" % (m2.database, name))
                if len(match) > 1:
                    self.log.error("有多个名为 %s 的流程，无法匹配" % (name,))
                if len(match) == 1:
                    m2.pipeline.id = cast_text(match[0].id)  # type: ignore
                else:
                    wulifang.manifest.request_user_edit(m, wait=True)
        if not m2.pipeline.id:
            self.log.info("无 CGTeamwork 流程匹配")
            return
        if not m.project.segment.name:
            (pipeline,) = database.pipeline.filter(
                (cgtwq.Field("#id") == m2.pipeline.id),
            )
            m.project.segment.name = cast_text(pipeline.name)  # type: ignore
            self.log.info("自动设置清单环节名称为 %s" % m.project.segment.name)
        if not m2.task.id:
            if m.shot.name:
                match = module.filter(
                    (cgtwq.Field("pipeline.id") == m2.pipeline.id)  # type: ignore
                    & (cgtwq.Field("shot.entity") == m.shot.name)
                )
                if len(match) == 1:
                    m2.task.id = match[0]
        if not m2.task.id:
            self.log.info("无 CGTeamwork 任务匹配")
            return
        entry = module.select(m2.task.id).to_entry()
        with_task(ctx, entry)

        ctx.create_instance(
            "CGTeamwork 任务: %s" % (entry["shot.entity"],),
            family="CGTeamwork 任务",
            work_file=obj,
        )
