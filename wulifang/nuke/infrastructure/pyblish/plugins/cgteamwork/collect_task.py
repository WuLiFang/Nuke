# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import os

import wulifang
from wulifang.vendor.cgtwq import desktop as cgtw, F, RowID
from wulifang.vendor.pyblish import api
from wulifang.infrastructure.cgteamwork.match_database import match_database

from .._context_manifest import context_manifest
from ._context_task import with_task, Task


class CollectTask(api.InstancePlugin):
    """获取工作文件对应的 CGTeamWork任务。"""

    order = api.CollectorOrder + 0.05
    label = "获取 CGTeamwork 任务"
    families = ["工作文件"]
    default_segment_name = "合成"

    def process(self, instance):
        # type: (api.Instance) -> None
        client = cgtw.current_client()
        if not client:
            self.log.info("未运行 CGTeamwork 桌面端，跳过相关检查")
            return
        obj = instance
        filename = os.path.basename(obj.name)
        ctx = instance.context
        m = context_manifest(obj)
        m2 = m.cgteamwork
        if not m2.database:
            if m.project.name:
                name = m.project.name
                match = list(match_database(client, name))
                if len(match) == 1:
                    m2.database = match[0]
                elif len(match) > 1:
                    self.log.info("有多个项目匹配名称 '%s'" % (name,))
                else:
                    self.log.info("无法通过项目名称 '%s' 匹配项目" % (name,))
        if not m2.database:
            try:
                m2.database = next(match_database(client, filename))
            except StopIteration:
                self.log.info("无法通过文件名 '%s' 匹配项目" % (filename,))
        if not m2.database:
            wulifang.manifest.request_user_edit(m, wait=True)
        if not m2.database:
            self.log.info("清单未指定 CGTeamwork 数据库")
            return
        if not m2.module:
            m2.module = "shot"

        if not m.shot.fps:
            try:
                for (fps,) in client.table(
                    "public",
                    "project",
                    "info",
                    filter_by=F("project.database").equal(m2.database),
                ).rows("project.frame_rate"):
                    m.shot.fps = float(fps)
                self.log.info("从 CGTeamwork 数据库获取了帧速率")
            except:
                pass

        if not m.project.name:
            for (name,) in client.table(
                "public",
                "project",
                "info",
                filter_by=F("project.database").equal(m2.database),
            ).rows("project.full_name"):
                m.project.name = name
                self.log.info("自动设置清单项目名称为 %s" % m.project.name)
        if not m2.pipeline.id:
            if m2.task.id:
                for (name,) in client.table(
                    m2.database,
                    m2.module,
                    "task",
                    filter_by=F("#id").equal(m2.task.id),
                ).rows("pipeline.id"):
                    m2.pipeline.id = name
            else:
                name = m.project.segment.name or self.default_segment_name
                self.log.info(
                    "清单未配置流程，自动从 '%s' 查找名为 '%s' 的流程"
                    % (m2.database, name)
                )
                match = [
                    id
                    for id, in client.pipeline.table(
                        m2.database,
                        filter_by=F("module")
                        .equal(m2.module)
                        .and_(F("pipeline.entity").equal(name)),
                    ).rows("pipeline.id")
                ]
                if len(match) > 1:
                    self.log.error("有多个名为 %s 的流程，无法匹配" % (name,))
                if len(match) == 1:
                    m2.pipeline.id = match[0]
                else:
                    wulifang.manifest.request_user_edit(m, wait=True)
        if not m2.pipeline.id:
            self.log.info("无 CGTeamwork 流程匹配")
            return
        if not m.project.segment.name:
            for (name,) in client.pipeline.table(
                m2.database, filter_by=F("#id").equal(m2.pipeline.id)
            ).rows("pipeline.entity"):
                m.project.segment.name = name
                self.log.info("自动设置清单环节名称为 %s" % m.project.segment.name)
        if not m2.task.id:
            if m.shot.name:
                match = [
                    id
                    for id, in client.table(
                        m2.database,
                        m2.module,
                        "task",
                        filter_by=F("pipeline.id")
                        .equal(m2.pipeline.id)
                        .and_(F("shot.entity").equal(m.shot.name)),
                    ).rows("#id")
                ]
                if len(match) == 1:
                    m2.task.id = match[0]
        if not m2.task.id:
            self.log.info("无 CGTeamwork 任务匹配")
            return
        task = Task(
            client,
            RowID(
                m2.database,
                m2.module,
                "task",
                m2.task.id,
            ),
        )
        with_task(ctx, task)
        ctx.create_instance(
            "CGTeamwork 任务: '%s'" % (m.shot.name,),
            family="CGTeamwork 任务",
            work_file=obj,
        )
