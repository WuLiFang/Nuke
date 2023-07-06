# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import os

import nuke

from wulifang._util import cast_str, cast_text, assert_isinstance, sanitize_filename


def dialog():
    """Split work file to multiple file by backdrop."""

    text_save_to = "保存至:"
    text_ask_if_create_new_folder = "目标文件夹不存在, 是否创建?"

    # Panel
    panel = nuke.Panel(cast_str("按 Backdrop 拆分文件"))
    _ = panel.addFilenameSearch(
        cast_str(text_save_to), cast_str(os.getenv("TEMP") or "")
    )
    if not panel.show():
        return

    # Save splitted .nk file
    save_path = cast_text(panel.value(cast_str(text_save_to))).rstrip("\\/")
    if not os.path.exists(save_path):
        if not nuke.ask(cast_str(text_ask_if_create_new_folder)):
            return
    dir_ = save_path + "/split_nk/"
    dir_ = os.path.normcase(dir_)
    if not os.path.exists(dir_):
        os.makedirs(dir_)
    untitled_count = 0
    for i in nuke.allNodes(cast_str("BackdropNode")):
        i = assert_isinstance(i, nuke.BackdropNode)
        title = sanitize_filename(cast_text(i[cast_str("label")].value()))
        if not title:
            untitled_count += 1
            title = "untitled_{0:03d}".format(untitled_count)
        filename = dir_ + title + ".nk"
        i.selectOnly()
        i.selectNodes()
        nuke.nodeCopy(cast_str(filename))
    _ = os.system('explorer "' + dir_ + '"')
