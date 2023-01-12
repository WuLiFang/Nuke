# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text

import hashlib
import os
import shutil

import wulifang
from wulifang.vendor.concurrent import futures

import nuke

from .._util import cast_binary, cast_text, iteritems, FileSequence
from ._gizmo import gizmo_to_group


def _hashed_dir(dir_path):
    # type: (Text) -> Text
    p = os.path.normcase(dir_path)
    parent, p = os.path.split(p)
    h = hashlib.sha256(parent.encode("utf-8")).hexdigest()
    return "%s.@%s" % (p, h[:8])


def _save_by_expr(cwd, file_dir, src_expr):
    # type: (Text, Text, Text) -> Text
    wulifang.message.info("正在打包: %s" % src_expr)
    src_dir, src_expr = os.path.split(src_expr)
    _dir_with_hash = _hashed_dir(src_dir)
    dst_dir = os.path.join(cwd, file_dir, _dir_with_hash)
    try:
        os.makedirs(dst_dir)
    except:
        pass
    seq = FileSequence(os.path.normcase(src_expr))
    executor = futures.ThreadPoolExecutor(max_workers=32)

    def _copy_file(i):
        # type: (Text) -> None
        src = os.path.join(src_dir, i)
        shutil.copy2(src, dst_dir)

    try:
        files = os.listdir(src_dir)
    except:
        wulifang.message.info("忽略: %s" % src_dir)
        files = []
    with executor:
        for _ in executor.map(_copy_file, (i for i in files if os.path.normcase(i) in seq)):  # type: ignore
            pass

    return "/".join((file_dir, _dir_with_hash, src_expr))


def pack_project():
    try:
        script_name = nuke.scriptName()
    except RuntimeError:
        nuke.message("请先保存工程".encode("utf-8"))
        return
    with nuke.Undo("打包工程"):
        project_dir_old = cast_text(nuke.value(b"root.project_directory"))
        script_dir = cast_text(os.path.dirname(script_name))
        nuke.Root()["project_directory"].setValue("[python {nuke.script_directory()}]")

        gizmo_count = 0
        for n in nuke.allNodes():
            if isinstance(n, nuke.Gizmo) and n.Class() not in nuke.knobChangeds:
                gizmo_to_group(n)
                gizmo_count += 1
        if gizmo_count:
            wulifang.message.info("将 %d 个 Gizmo 转为了 Group" % gizmo_count)

        file_dir = os.path.basename(cast_text(script_name)) + ".files"
        for n in nuke.allNodes():
            for _, k in iteritems(n.knobs()):
                if isinstance(k, nuke.File_Knob):
                    old_src = cast_text(k.getText())
                    if not old_src or old_src.startswith(file_dir):
                        continue
                    new_src = _save_by_expr(
                        script_dir, file_dir, os.path.join(project_dir_old, old_src)
                    )
                    k.setText(cast_binary(new_src))

        wulifang.message.info("项目打包完毕，相关文件存放于 %s" % file_dir)
