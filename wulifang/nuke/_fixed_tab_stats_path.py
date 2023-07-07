# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import io
import os

import nuke

from wulifang._util import cast_str, cast_text
import wulifang.nuke


def init_gui():
    path_input = cast_text(os.getenv("NUKE_TAB_STATS_DIR_4F14D65B"))
    if nuke.NUKE_VERSION_MAJOR < 11 or path_input == "-":
        return
    p = os.path.expanduser(path_input or "~/.nuke/com.wlf-studio.tab-stats")
    try:
        os.mkdir(p)
    except OSError:
        pass
    with io.open(p + "/init.py", "w", encoding="utf-8") as f:
        f.write(
            """\
# -*- coding=UTF-8 -*-
# 此文件由吾立方插件自动生成, 不要编辑。 DO NOT EDIT
#
# nuke 会把 tab 菜单使用数据文件 (tab_stats.dat) 保存在第一个插件的位置，
# 通过不含任何代码的此插件将统计文件存放路径固定。
# 
# 通过环境变量设置:
#   NUKE_TAB_STATS_DIR_4F14D65B: 保存目录
#     默认为 "~/.nuke/com.wlf-studio.tab-stats"。为单个减号(-)时此功能禁用。
"""
        )

    p_str = cast_str(p)

    def on_user_create():
        if (nuke.pluginPath() or ("",))[0] != p_str:
            nuke.pluginAddPath(p_str)

    wulifang.nuke.callback.on_user_create(on_user_create)
