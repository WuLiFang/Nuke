# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import io
import tempfile
import sys

import nuke

from wulifang.nuke._util import iter_deep_all_nodes, Progress
from wulifang._util import cast_str, cast_text, cast_binary
import wulifang.nuke

_POSSIBLE_ENCODING = (
    sys.getdefaultencoding(),
    sys.getfilesystemencoding(),
    "gbk",
)


def _to_utf8(s):
    # type: (bytes) -> bytes
    for i in _POSSIBLE_ENCODING:
        try:
            return s.decode(i).encode("utf-8")
        except:
            # ignore all error
            pass
    return s.decode("utf-8", "backslashreplace").encode("utf-8")


def _fix_node(n):
    # type: (nuke.Node) -> None
    error_knobs = set()  # type: set[nuke.String_Knob]
    for k in n.allKnobs():
        if isinstance(k, nuke.String_Knob):
            try:
                k.value()
            except UnicodeDecodeError:
                error_knobs.add(k)
    if not error_knobs:
        # nothing to fix
        return

    n.selectOnly()
    fd, name = tempfile.mkstemp(".nk", "clipboard-")
    try:
        nuke.nodeCopy(cast_str(name))
        with io.open(name, "rb") as f:
            raw_data = f.read()
        with io.open(name, "wb") as f:
            f.write(_to_utf8(raw_data))
        template = nuke.nodePaste(cast_str(name))
    finally:
        os.close(fd)
        os.unlink(name)
    for k in error_knobs:
        k.fromScript(template[k.name()].toScript())
    nuke.delete(template)


def fix_unicode_decode_error():
    with Progress("修复字符解码错误") as p:
        for n in iter_deep_all_nodes():
            _fix_node(n)
            p.set_message(cast_text(n.fullName()))
            p.increase()


def _on_backdrop_create():
    try:
        cast_binary(nuke.value(cast_str("label"))).decode("utf-8")
    except UnicodeDecodeError:
        wulifang.message.info(
            "检测到 %s 有字符解码错误，建议尝试 文件 - 修复字符解码错误 功能"
            % (cast_text(nuke.thisNode().fullName()),)
        )
    except:
        pass


def init_gui():
    wulifang.nuke.callback.on_create(_on_backdrop_create, node_class="BackdropNode")
