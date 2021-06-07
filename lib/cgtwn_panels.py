# -*- coding=UTF-8 -*-
"""Panels for `cgtwn`.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import webbrowser

import nuke

import cgtwq
import cgtwq.core
from wlf.progress import CancelledError, progress
from wlf.uitools import Tray
import cast_unknown as cast

LOGGER = logging.getLogger(__name__)


def dialog_login():
    """Login teamwork."""

    client = cgtwq.DesktopClient()
    if client.is_logged_in():
        client.connect()
        Tray.message("CGTeamWork", "登录成功")
        return
    account = "帐号"
    password = "密码"
    panel = nuke.Panel(b"")
    _ = panel.addSingleLineInput(cast.binary(account), b"")
    _ = panel.addPasswordInput(cast.binary(password), b"")

    while True:
        confirm = panel.show()
        if confirm:
            try:
                cgtwq.core.CONFIG["DEFAULT_TOKEN"] = cgtwq.login(
                    panel.value(cast.binary(account)) or "",
                    panel.value(cast.binary(password)) or "",
                )
            except ValueError:
                Tray.message("CGTeamWork", "登录失败")
                continue
            Tray.message("CGTeamWork", "登录成功")
        break


def dialog_create_dirs():
    """A dialog for create dirs from cgtwq."""

    folder_input_name = "输出文件夹"
    database_input_name = "数据库"
    prefix_input_name = "镜头名前缀限制"
    panel = nuke.Panel(cast.binary("为项目创建文件夹"))
    _ = panel.addSingleLineInput(cast.binary(database_input_name), b"proj_qqfc_2017")
    _ = panel.addSingleLineInput(cast.binary(prefix_input_name), b"")
    _ = panel.addFilenameSearch(cast.binary(folder_input_name), b"E:/temp")
    confirm = panel.show()
    if not confirm:
        return

    try:
        database = cast.text(panel.value(cast.binary(database_input_name)))
        save_path = panel.value(cast.binary(folder_input_name))
        prefix = panel.value(cast.binary(prefix_input_name))
        if not save_path:
            return

        for _ in progress(
            [
                "连接CGTeamWork...",
            ],
            "创建文件夹",
        ):
            try:
                select = cgtwq.Database(database)["shot_task"].filter(
                    cgtwq.Field("pipeline") == "合成"
                )
                for name in progress(select["shot.shot"], "创建文件夹"):
                    if not name or not name.startswith(prefix):
                        continue
                    _path = os.path.join(save_path, name)
                    if not os.path.exists(_path):
                        os.makedirs(_path)
            except cgtwq.IDError as ex:
                nuke.message(cast.binary("找不到对应条目\n{}".format(ex)))
                return

        _ = webbrowser.open(save_path)
    except CancelledError:
        LOGGER.debug("用户取消创建文件夹")
