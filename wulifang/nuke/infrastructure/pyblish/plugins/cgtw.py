# -*- coding=UTF-8 -*-
"""CGTeamWork pyblish plug-in.  """

from __future__ import absolute_import, division, print_function, unicode_literals
import traceback


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import List, Text, Tuple


import logging
import os
import shutil
import webbrowser
import wulifang

import cast_unknown as cast
import nuke
import wulifang.filename
from wulifang.nuke.infrastructure.wlf_write_node import wlf_write_node
from wulifang.nuke.infrastructure.cgteamwork.entry_from_shot import entry_from_shot
from wulifang.nuke.infrastructure.cgteamwork.import_task_video import import_task_video
from wulifang.nuke.infrastructure.recover_modifield_flag import recover_modifield_flag
from wulifang.vendor import cgtwq
from wulifang.vendor.pyblish import api


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


def _context_task(context):
    # type: (api.Context) -> Tuple[cgtwq.Entry, Text]
    """Get task from context"""
    try:
        entry = context.data["taskEntry"]
        shot = context.data["shot"]
        return entry, shot
    except KeyError:
        raise ValueError("无对应任务")


class CollectTask(api.InstancePlugin):
    """获取Nuke文件对应的CGTeamWork任务."""

    order = api.CollectorOrder + 0.05
    label = "获取对应任务"
    families = ["Nuke文件"]

    def process(self, instance):
        shot = wulifang.filename.get_shot(instance.name)
        ctx = instance.context
        try:
            entry = entry_from_shot(shot)
            instance.context.data["taskEntry"] = entry
            instance.context.data["shot"] = shot
            instance.context.create_instance(
                "组长状态: {}".format(entry["leader_status"]), family="组长状态"
            )
        except ValueError:
            raise ValueError("无法在数据库中找到对应任务: %s" % shot)

        try:
            instance.context.data["workfileFileboxInfo"] = entry.filebox.get("workfile")
        except:
            raise ValueError("找不到标识为workfile的文件框 请联系管理员进行设置")


class CollectUser(api.ContextPlugin):
    """获取当前登录的用户帐号."""

    order = api.CollectorOrder
    label = "获取当前用户"

    def process(self, context):
        name = cgtwq.ACCOUNT.select(cgtwq.get_account_id()).to_entry()["name"]

        context.data["artist"] = name
        context.data["accountID"] = cgtwq.get_account_id()
        context.create_instance("制作者: {}".format(name), family="制作者")


import glob


class CollectFX(api.ContextPlugin):
    """获取特效素材."""

    order = api.CollectorOrder + 0.1
    label = "获取特效素材"

    def process(self, context):
        entry, _ = _context_task(context)
        try:
            filebox = entry.filebox.get("fx")
        except ValueError:
            self.log.warn("找不到标识为 fx 的文件框，无法获取特效文件。可联系管理员进行设置")
            return
        wulifang.message.debug("fx filebox path: %s" % filebox.path)
        try:
            match = next(glob.iglob(filebox.path + "/*"))
            dir_ = os.path.dirname(match)
            context.create_instance("特效素材", folder=dir_, family="特效素材")
        except StopIteration:
            self.log.info("无特效素材")


class OpenFolder(api.InstancePlugin):
    """打开非空的文件夹."""

    order = api.ValidatorOrder
    label = "打开素材文件夹"
    families = ["特效素材"]

    def process(self, instance):
        try:
            webbrowser.open(instance.data["folder"])
        except:
            traceback.print_exc()


class ValidateArtist(api.InstancePlugin):
    """检查任务是否分配给当前用户。"""

    order = api.ValidatorOrder
    label = "检查制作者"
    families = ["制作者"]

    def process(self, instance):
        ctx = instance.context
        context = instance.context
        entry, _ = _context_task(instance.context)

        current_id = cast.text(context.data["accountID"])
        current_artist = cast.text(context.data["artist"])

        id_ = cast.text(entry["account_id"])
        if current_id not in id_.split(","):
            raise ValueError("用户不匹配: %s -> %s" % (current_artist, entry["artist"]))


class ValidateLeaderStatus(api.InstancePlugin):
    """检查任务是否允许提交。"""

    order = api.ValidatorOrder
    label = "检查组长状态"
    families = ["组长状态"]

    def process(self, instance):
        context = instance.context

        entry, _ = _context_task(instance.context)

        status = entry["leader_status"]
        if status in ("Approve", "Close"):
            raise ValueError("任务状态为 %s，禁止提交" % status)


class ValidateFrameRange(api.InstancePlugin):
    """检查帧范围是否匹配上游."""

    order = api.ValidatorOrder
    label = "检查帧范围"
    families = ["帧范围"]

    def process(self, instance):
        task, shot = _context_task(instance.context)

        with recover_modifield_flag():
            try:
                n = import_task_video(task, shot, "animation_videos")
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


class ValidateFPS(api.InstancePlugin):
    """检查帧速率是否匹配数据库设置."""

    order = api.ValidatorOrder
    label = "检查帧速率"
    families = ["帧速率"]

    def process(self, instance):
        entry, shot = _context_task(instance.context)

        database = entry.module.database
        fps = database.metadata["fps"]
        if not fps:
            self.log.warning("数据库未设置帧速率: %s", database.name)
        else:
            current_fps = instance.data["fps"]
            if float(cast.text(fps)) != current_fps:
                raise ValueError("帧速率不一致: %s -> %s" % (current_fps, fps))


class UploadPrecompFile(api.InstancePlugin):
    """上传相关预合成文件至CGTeamWork."""

    order = api.IntegratorOrder
    label = "上传预合成文件"
    families = ["Nuke文件"]

    def process(self, instance):
        dest = instance.context.data["workfileFileboxInfo"].path + "/"

        for n in nuke.allNodes(b"Precomp"):
            src = cast.text(nuke.filename(n))
            if src.startswith(dest.replace("\\", "/")):
                continue
            n["file"].setValue(_copy_file(src, dest))
        _ = nuke.scriptSave()


class UploadWorkFile(api.InstancePlugin):
    """上传工作文件至CGTeamWork."""

    order = api.IntegratorOrder + 0.1
    label = "上传工作文件"
    families = ["Nuke文件"]

    def process(self, instance):
        dest = instance.context.data["workfileFileboxInfo"].path + "/"
        workfile = instance.data["name"]

        _ = _copy_file(workfile, dest)


class UploadJPG(api.InstancePlugin):
    """上传单帧至CGTeamWork."""

    order = api.IntegratorOrder
    label = "上传单帧"
    families = ["Nuke文件"]

    def process(self, instance):
        try:
            context = instance.context
            entry, shot = _context_task(context)

            n = wlf_write_node()
            path = cast.text(nuke.filename(cast.not_none(n.node(b"Write_JPG_1"))))
            dest = entry.filebox.get("review").path + "/{}.jpg".format(shot)
            wulifang.message.debug("upload src: %s -> %s" % (path, dest))

            _ = _copy_file(path, dest)

            context.data["submitImage"] = entry.set_image(dest)
        except:
            traceback.print_exc()
            raise


class SubmitTask(api.ContextPlugin):
    """在CGTeamWork上提交任务."""

    order = api.IntegratorOrder + 0.1
    label = "提交任务"

    def process(self, context):
        entry, shot = _context_task(context)

        if entry["leader_status"] == "Check":
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

        entry.flow.submit(filenames=tuple(filenames), message=message)
