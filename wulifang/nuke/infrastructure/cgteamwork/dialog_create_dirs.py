# -*- coding=UTF-8 -*-
"""Panels for `cgtwn`.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import webbrowser

import nuke
import wulifang

from wulifang.vendor.cgtwq import desktop as cgtw, F
from wulifang.vendor.wlf.progress import CancelledError, progress
from wulifang._util import cast_str, cast_text


def dialog_create_dirs():
    """A dialog for create dirs from cgtwq."""

    folder_input_name = "输出文件夹"
    database_input_name = "数据库"
    prefix_input_name = "镜头名前缀限制"
    panel = nuke.Panel(cast_str("为项目创建文件夹"))
    _ = panel.addSingleLineInput(cast_str(database_input_name), cast_str("proj_"))
    _ = panel.addSingleLineInput(cast_str(prefix_input_name), cast_str(""))
    _ = panel.addFilenameSearch(cast_str(folder_input_name), cast_str("E:/temp"))
    confirm = panel.show()
    if not confirm:
        return
    client = cgtw.current_client()
    if not client:
        wulifang.message.error("无法连接 CGTeamwork 客户端，请检查客户端是否运行")
        return
    try:
        database = cast_text(panel.value(cast_str(database_input_name)))
        save_path = cast_text(panel.value(cast_str(folder_input_name)))
        prefix = cast_text(panel.value(cast_str(prefix_input_name)))
        if not save_path:
            return

        for _ in progress(
            [
                "连接CGTeamWork...",
            ],
            "创建文件夹",
        ):

            match_count = 0
            for (name,) in client.table(
                database, "shot", "task", filter_by=F("pipeline").equal("合成")
            ).rows("shot.entity"):
                if not name or not name.startswith(prefix):
                    continue
                match_count += 1
                _path = os.path.join(save_path, name)
                if not os.path.exists(_path):
                    os.makedirs(_path)
            if match_count == 0:
                nuke.message(cast_str("找不到对应条目"))
                return
        _ = webbrowser.open(save_path)
    except CancelledError:
        wulifang.message.debug("用户取消创建文件夹")
