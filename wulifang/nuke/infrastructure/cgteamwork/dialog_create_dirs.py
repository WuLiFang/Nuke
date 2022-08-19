# -*- coding=UTF-8 -*-
"""Panels for `cgtwn`.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import webbrowser

import nuke
import wulifang

from wulifang.vendor import cgtwq
from wulifang.vendor.wlf.progress import CancelledError, progress
import wulifang.vendor.cast_unknown as cast


def dialog_create_dirs():
    """A dialog for create dirs from cgtwq."""

    folder_input_name = "输出文件夹"
    database_input_name = "数据库"
    prefix_input_name = "镜头名前缀限制"
    panel = nuke.Panel(cast.binary("为项目创建文件夹"))
    _ = panel.addSingleLineInput(cast.binary(database_input_name), b"proj_")
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
                select = (
                    cgtwq.Database(database)
                    .module("shot")
                    .filter(cgtwq.Field("pipeline") == "合成")
                )
                for name in progress(select["shot.entity"], "创建文件夹"):
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
        wulifang.message.debug("用户取消创建文件夹")
