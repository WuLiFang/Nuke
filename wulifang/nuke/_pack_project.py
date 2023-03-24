# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional

import codecs
import datetime
import hashlib
import json
import os
import shutil

import wulifang
from wulifang.vendor.concurrent import futures

import nuke

from .._util import TZ_CHINA, FileSequence, cast_binary, cast_text, iteritems
from ._gizmo import gizmo_to_group


class _Context(object):
    def __init__(self):
        self.project_dir_old = cast_text(nuke.value(b"root.project_directory"))
        self.script_name = nuke.scriptName()
        self.script_dir = cast_text(os.path.dirname(self.script_name))
        self.file_dir = cast_text(self.script_name) + ".files"
        self.file_dir_base = os.path.basename(self.file_dir)
        try:
            os.makedirs(self.file_dir)
        except:
            pass
        self.log_file = codecs.open(
            os.path.join(self.file_dir, "工程打包日志.txt"),
            "a",
            encoding="utf-8",
        )
        self._log("开始")
        self._log("工程文件：%s" % self.script_name)
        self._log("原工程目录：%s" % self.project_dir_old)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.log_file.close()

    def _log(self, msg):
        # type: (Text) -> None
        self.log_file.write(
            "[%s] %s\r\n" % (datetime.datetime.now(TZ_CHINA).isoformat(), msg)
        )

    def log(self, msg):
        # type: (Text) -> None
        wulifang.message.info(msg)
        self._log(msg)


def _hashed_dir(dir_path):
    # type: (Text) -> Text
    parent, p = os.path.split(dir_path)
    h = hashlib.sha256(os.path.normpath(parent).encode("utf-8")).hexdigest()
    return "%s.@%s" % (p, h[:8])


def _is_weak_same(a, b):
    # type: (Text, Text) -> bool
    try:
        stat_a = os.stat(a)
        stat_b = os.stat(b)
    except:
        return False

    return (
        stat_a.st_size == stat_b.st_size and abs(stat_a.st_mtime - stat_b.st_mtime) < 1
    )


def _save_by_expr(ctx, src_expr):
    # type: (_Context, Text) -> Text
    src_dir, src_base = os.path.split(src_expr)

    _dir_with_hash = _hashed_dir(src_dir)
    dst_dir = os.path.join(ctx.file_dir, _dir_with_hash)

    try:
        os.makedirs(dst_dir)
    except:
        pass
    with codecs.open(dst_dir + ".json", "w", encoding="utf-8") as f:
        json.dump(
            {"sourcePath": src_expr},
            f,
            indent=2,
            ensure_ascii=False,
        )

    try:
        files = os.listdir(src_dir)
    except:
        ctx.log("目录无法访问: %s" % src_dir)
        files = []

    seq = FileSequence(os.path.normcase(src_base))
    executor = futures.ThreadPoolExecutor(max_workers=32)

    def _copy_file(i):
        # type: (Text) -> None
        src = os.path.join(src_dir, i)
        dst = os.path.join(dst_dir, i)
        if _is_weak_same(src, dst):
            return
        shutil.copy2(src, dst)

    with executor:
        for _ in executor.map(_copy_file, (i for i in files if os.path.normcase(i) in seq)):  # type: ignore
            pass

    return "/".join((ctx.file_dir_base, _dir_with_hash, src_base))


def _iter_deep_all_nodes(root=None):
    # type: (Optional[nuke.Group]) -> ...
    for n in (root or nuke.Root()).nodes():
        if isinstance(n, nuke.Group):
            for i in _iter_deep_all_nodes(n):
                yield i
        yield n


def pack_project():
    try:
        nuke.scriptName()
    except RuntimeError:
        nuke.message("请先保存工程".encode("utf-8"))
        return

    with nuke.Undo("打包工程"), _Context() as ctx:
        nuke.Root()[b"project_directory"].setValue("[python {nuke.script_directory()}]")

        for n in _iter_deep_all_nodes():
            if isinstance(n, nuke.Gizmo):
                name = cast_text(n.fullName())
                if n.Class() in nuke.knobChangeds:
                    ctx.log("%s: 此类型节点有脚本回调，无法转为 Group" % (name,))
                    continue
                gizmo_to_group(n)
                ctx.log("将 %s 转为了 Group" % (name,))

        for n in _iter_deep_all_nodes():
            for _, k in iteritems(n.knobs()):
                if isinstance(k, nuke.File_Knob):
                    old_src = cast_text(k.getText())
                    if not old_src or old_src.startswith(ctx.file_dir_base):
                        continue
                    ctx.log("打包文件: %s.%s: %s" % (n.fullName(), k.name(), old_src))
                    new_src = _save_by_expr(
                        ctx, os.path.join(ctx.project_dir_old, old_src)
                    )
                    k.setText(cast_binary(new_src))
        ctx.log("完成")
        nuke.message(
            ("项目打包完毕\n文件保存目录： %s\n工程内的文件路径已全部替换，请检查后保存" % (ctx.file_dir,)).encode(
                "utf-8"
            )
        )