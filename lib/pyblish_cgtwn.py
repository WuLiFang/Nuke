# -*- coding=UTF-8 -*-
"""CGTeamWork pyblish plug-in.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import webbrowser

import nuke
import pyblish.api

import cast_unknown as cast
import cgtwq
import nuketools
from cgtwn import Task
from filetools import get_shot
from node import wlf_write_node
import shutil
from wlf.fileutil import copy
import logging

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, List


_LOGGER = logging.getLogger(__name__)


def _copy_file(src, dst):
    src = cast.text(src)
    dst = cast.text(dst)
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(dst))
    _LOGGER.info("复制:\n\t\t%s\n\t->\t%s", src, dst)
    try:
        return shutil.copy2(src, dst)
    except shutil.Error:
        return dst


class TaskMixin(object):
    """Provide task related method."""

    def get_task(self, context):
        """Get task from context"""
        try:
            task = context.data["task"]
            assert isinstance(task, Task), type(task)
            return task
        except KeyError:
            raise ValueError("无对应任务")


class CollectTask(pyblish.api.InstancePlugin):
    """获取Nuke文件对应的CGTeamWork任务."""

    order = pyblish.api.CollectorOrder
    label = "获取对应任务"
    families = ["Nuke文件"]

    def process(self, instance):

        assert isinstance(instance, pyblish.api.Instance)

        client = cgtwq.DesktopClient()
        if client.is_logged_in():
            client.connect()

        shot = get_shot(instance.name)
        try:
            task = Task.from_shot(shot)
            instance.context.data["task"] = task
            instance.context.create_instance(
                "组长状态: {}".format(task["leader_status"]), family="组长状态"
            )
        except ValueError:
            raise ValueError("无法在数据库中找到对应任务: %s" % shot)
        self.log.info("任务 %s", task)

        try:
            instance.context.data["workfileFileboxInfo"] = task.filebox.get("workfile")
        except:
            raise ValueError("找不到标识为workfile的文件框 请联系管理员进行设置")


class CollectUser(pyblish.api.ContextPlugin):
    """获取当前登录的用户帐号."""

    order = pyblish.api.CollectorOrder
    label = "获取当前用户"

    def process(self, context):
        assert isinstance(context, pyblish.api.Context)

        name = cgtwq.ACCOUNT.select(cgtwq.get_account_id()).to_entry()["name"]

        context.data["artist"] = name
        context.data["accountID"] = cgtwq.get_account_id()
        context.create_instance("制作者: {}".format(name), family="制作者")


class CollectFX(TaskMixin, pyblish.api.ContextPlugin):
    """获取特效素材."""

    order = pyblish.api.CollectorOrder + 0.1
    label = "获取特效素材"

    def process(self, context):
        task = self.get_task(context)
        assert isinstance(task, Task)
        try:
            filebox = task.filebox.get("fx")
        except ValueError:
            self.log.warn("找不到标识为 fx 的文件框，无法获取特效文件。可联系管理员进行设置")
            return
        dir_ = filebox.path
        context.create_instance(
            "有特效素材" if os.listdir(dir_) else "无特效素材", folder=dir_, family="特效素材"
        )


class OpenFolder(pyblish.api.InstancePlugin):
    """打开非空的文件夹."""

    order = pyblish.api.ValidatorOrder
    label = "打开素材文件夹"
    families = ["特效素材"]

    def process(self, instance):
        if os.listdir(instance.data["folder"]):
            _ = webbrowser.open(instance.data["folder"])


class ValidateArtist(TaskMixin, pyblish.api.InstancePlugin):
    """检查任务是否分配给当前用户。"""

    order = pyblish.api.ValidatorOrder
    label = "检查制作者"
    families = ["制作者"]

    def process(self, instance):
        assert isinstance(instance, pyblish.api.Instance)
        context = instance.context
        task = self.get_task(instance.context)
        assert isinstance(task, Task)

        current_id = cast.text(context.data["accountID"])
        current_artist = cast.text(context.data["artist"])

        id_ = cast.text(task["account_id"])
        if current_id not in id_.split(","):
            raise ValueError("用户不匹配: %s -> %s" % (current_artist, task["artist"]))


class ValidateLeaderStatus(TaskMixin, pyblish.api.InstancePlugin):
    """检查任务是否允许提交。"""

    order = pyblish.api.ValidatorOrder
    label = "检查组长状态"
    families = ["组长状态"]

    def process(self, instance):
        assert isinstance(instance, pyblish.api.Instance)
        context = instance.context

        task = self.get_task(instance.context)
        assert isinstance(task, Task)

        status = task["leader_status"]
        if status in ("Approve", "Close"):
            raise ValueError("任务状态为 %s，禁止提交" % status)


class ValidateFrameRange(TaskMixin, pyblish.api.InstancePlugin):
    """检查帧范围是否匹配上游."""

    order = pyblish.api.ValidatorOrder
    label = "检查帧范围"
    families = ["帧范围"]

    def process(self, instance):
        assert isinstance(instance, pyblish.api.Instance)
        task = self.get_task(instance.context)
        assert isinstance(task, Task)

        with nuketools.keep_modifield_status():
            try:
                n = task.import_video("animation_videos")
            except ValueError:
                raise ValueError(
                    "找不到标识为 animation_videos 的文件框，无法获取动画文件。可联系管理员进行设置",
                )
            if not n:
                raise ValueError("找不到对应的动画视频文件")
        upstream_framecount = int(n[b"last"].value() - n[b"first"].value() + 1)
        current_framecount = int(instance.data["last"] - instance.data["first"] + 1)
        if upstream_framecount != current_framecount:
            raise ValueError(
                "工程帧数和上游不一致: %s -> %s" % (upstream_framecount, current_framecount),
            )


class ValidateFPS(TaskMixin, pyblish.api.InstancePlugin):
    """检查帧速率是否匹配数据库设置."""

    order = pyblish.api.ValidatorOrder
    label = "检查帧速率"
    families = ["帧速率"]

    def process(self, instance):
        task = self.get_task(instance.context)
        assert isinstance(task, Task)

        database = task.module.database
        fps = database.get_data("fps", is_user=False)
        if not fps:
            self.log.warning("数据库未设置帧速率: %s", database.name)
        else:
            current_fps = instance.data["fps"]
            if float(cast.text(fps)) != current_fps:
                raise ValueError("帧速率不一致: %s -> %s" % (current_fps, fps))


class UploadPrecompFile(TaskMixin, pyblish.api.InstancePlugin):
    """上传相关预合成文件至CGTeamWork."""

    order = pyblish.api.IntegratorOrder
    label = "上传预合成文件"
    families = ["Nuke文件"]

    def process(self, instance):
        assert isinstance(instance, pyblish.api.Instance)
        dest = instance.context.data["workfileFileboxInfo"].path + "/"

        for n in nuke.allNodes(b"Precomp"):
            src = cast.text(nuke.filename(n))
            if src.startswith(dest.replace("\\", "/")):
                continue
            n["file"].setValue(_copy_file(src, dest))
        _ = nuke.scriptSave()


class UploadWorkFile(TaskMixin, pyblish.api.InstancePlugin):
    """上传工作文件至CGTeamWork."""

    order = pyblish.api.IntegratorOrder + 0.1
    label = "上传工作文件"
    families = ["Nuke文件"]

    def process(self, instance):
        assert isinstance(instance, pyblish.api.Instance)
        dest = instance.context.data["workfileFileboxInfo"].path + "/"
        workfile = instance.data["name"]

        _ = _copy_file(workfile, dest)


class UploadJPG(TaskMixin, pyblish.api.InstancePlugin):
    """上传单帧至CGTeamWork."""

    order = pyblish.api.IntegratorOrder
    label = "上传单帧"
    families = ["Nuke文件"]

    def process(self, instance):
        context = instance.context
        task = self.get_task(context)
        assert isinstance(task, Task)

        n = wlf_write_node()
        assert isinstance(n, nuke.Group)
        path = cast.text(nuke.filename(cast.not_none(n.node(b"Write_JPG_1"))))
        dest = task.filebox.get("review").path + "/{}.jpg".format(task.shot)

        _ = copy(path, dest)

        context.data["submitImage"] = task.set_image(dest)


class SubmitTask(TaskMixin, pyblish.api.ContextPlugin):
    """在CGTeamWork上提交任务."""

    order = pyblish.api.IntegratorOrder + 0.1
    label = "提交任务"

    def process(self, context):
        task = self.get_task(context)
        assert isinstance(task, Task)

        if task["leader_status"] == "Check":
            self.log.info("任务已经是检查状态, 无需提交。")
            return

        note = nuke.getInput(
            "CGTeamWork任务提交备注(Cancel则不提交)".encode("utf-8"),
            b"",
        )

        if note is None:
            self.log.info("用户选择不提交任务。")
            return
        note = cast.text(note)

        message = cgtwq.Message(note)
        filenames = []  # type: List[Text]
        submit_image = context.data.get("submitImage")
        if submit_image:
            filenames.append(cast.text(submit_image.path))
            message.images.append(submit_image)  # type: ignore

        task.flow.submit(filenames=tuple(filenames), message=message)
