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
import re


from .._util import cast_binary, cast_text, iteritems


def _hashed_dir(dir_path):
    # type: (Text) -> Text
    p = os.path.normcase(dir_path)
    parent, p = os.path.split(p)
    h = hashlib.sha256(parent.encode("utf-8")).hexdigest()
    return "%s.@%s" % (p, h[:8])


class FilenameMatcher(object):
    expression_number_pattern = re.compile(r"%0\d*d|#+|\d+")
    actual_number_pattern = re.compile(r"\d+")
    repl = "⯒"

    def __init__(self, expr):
        # type: (Text) -> None
        self._target = self.expression_number_pattern.sub(
            self.repl,
            os.path.normcase(expr),
        )

    def match(self, v):
        # type: (Text) -> bool
        return (
            self.actual_number_pattern.sub(self.repl, os.path.normcase(v))
            == self._target
        )


def _save_by_expr(cwd, file_dir, src_expr):
    # type: (Text, Text, Text) -> Text
    if not src_expr or src_expr.startswith(file_dir):
        return src_expr
    src_dir, src_expr = os.path.split(src_expr)
    _dir_with_hash = _hashed_dir(src_dir)
    dst_dir = os.path.join(cwd, file_dir, _dir_with_hash)
    try:
        os.makedirs(dst_dir)
    except:
        pass
    wulifang.message.info("正在打包: %s" % src_dir)
    m = FilenameMatcher(src_expr)
    executor = futures.ThreadPoolExecutor(max_workers=32)

    def _copy_file(i):
        # type: (Text) -> None
        shutil.copy2(os.path.join(src_dir, i), dst_dir)
    try:
        files = os.listdir(src_dir)
    except:
        wulifang.message.info("忽略: %s" % src_dir)
        files = []
    with executor:
        for _ in executor.map(_copy_file, (i for i in files if m.match(i))):  # type: ignore
            pass

    return "/".join((file_dir, _dir_with_hash, src_expr))


def pack_project():
    script_name = nuke.scriptName()
    if not script_name:
        nuke.message("请先保存工程".encode("utf-8"))
        return
    with nuke.Undo("打包工程"):
        script_dir = cast_text(os.path.dirname(script_name))
        nuke.Root()["project_directory"].setValue("[python {nuke.script_directory()}]")
        file_dir = "files"
        for n in nuke.allNodes():
            for _, k in iteritems(n.knobs()):
                if isinstance(k, nuke.File_Knob):
                    k.setText(
                        cast_binary(
                            _save_by_expr(script_dir, file_dir, cast_text(k.getText()))
                        )
                    )
    wulifang.message.info("项目打包完毕，可能还有 Gizmo 需要转为 Group")
