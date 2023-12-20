# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import re
import logging

import nuke

import wulifang.nuke
from wulifang._util import (
    cast_text,
    cast_str,
    assert_isinstance,
    is_ascii,
    assert_not_none,
    lazy_getter,
)
from wulifang.nuke._util import (
    Progress,
    knob_of,
    parse_file_input,
    create_node,
)
from wulifang.vendor.six.moves import urllib_parse

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Iterator, Protocol, AnyStr, Optional

    class _Action(Protocol):
        def do(self, ctx):
            # type: (_FileContext) -> None
            pass

else:

    class _Action:
        pass


_LOGGER = logging.getLogger(__name__)


def _should_ignore(data):
    # type: (Text) -> bool
    if "\n" in data:
        return True
    return False


def _resolve_file_input_by_path(path):
    # type: (Text) -> Iterator[Text]
    if os.path.isdir(path):
        for dirpath, _, _ in os.walk(path):
            dirpath = dirpath.replace("\\", "/")
            for i in nuke.getFileNameList(cast_str(dirpath)):
                yield "{}/{}".format(dirpath, cast_text(i))
    else:
        yield path


def _resolve_file_input(data):
    # type: (Text) -> Iterator[Text]

    url = urllib_parse.urlparse(data)
    if url.scheme == "file":
        for i in _resolve_file_input_by_path(urllib_parse.unquote(url.path)):
            yield i
    else:
        for i in _resolve_file_input_by_path(data):
            yield i


class Result:
    def __init__(self):
        self.nodes = []  # type: list[nuke.Node]
        self.prevent_default = False


class _FileContext:
    class Cancelled(RuntimeError):
        def __init__(self):
            RuntimeError.__init__(self, "cancelled")

    def __init__(self, __res, __file_input):
        # type: (Result,Text) -> None
        self.res = __res
        self.file = parse_file_input(__file_input)
        _, ext = os.path.splitext(self.file.name())
        self.ext = ext
        self.ext_lower = ext.lower()

    def match_ext(self, *expected):
        # type: (Text) -> bool

        return any(self.ext_lower == i.lower() for i in expected)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # type: (Optional[type], Optional[Exception], Optional[object]) -> bool

        if self.res.nodes or exc_value:
            self.res.prevent_default = True
        if exc_type is self.Cancelled:
            return True
        return False


class _ImportDeepEXR(_Action):
    def do(self, ctx):
        # type: (_FileContext) -> None
        if not ctx.match_ext(".exr"):
            return
        n = nuke.nodes.DeepRead()
        assert_isinstance(n[cast_str("file")], nuke.File_Knob).fromUserText(
            cast_str(ctx.file.raw())
        )
        if n.hasError():
            nuke.delete(n)
            return
        ctx.res.nodes.append(n)


def _ext_by_plugin(__dir):
    # type: (Text) -> Iterator[Text]
    try:
        files = os.listdir(__dir)
    except OSError:
        return

    for file in files:
        s = file.lower()
        if "reader" not in s:
            continue
        yield ".%s" % (s[: s.index("reader")],)


class _ImportAny(_Action):
    @lazy_getter
    def _known_ext():
        return set(_ext_by_plugin(os.path.join(cast_text(nuke.EXE_PATH), "../plugins")))

    def do(self, ctx):
        # type: (_FileContext) -> None
        if not ctx.match_ext(*self._known_ext()):
            ctx.res.nodes.append(
                create_node(
                    "StickyNote",
                    label="未支持导入此文件类型（%s）:\n%s" % (ctx.ext, ctx.file.raw()),
                )
            )
            return

        n = nuke.createNode(cast_str("Read"))
        assert_isinstance(n[cast_str("file")], nuke.File_Knob).fromUserText(
            cast_str(ctx.file.raw())
        )
        if n.hasError():
            nuke.delete(n)
            return
        ctx.res.nodes.append(n)
        raise ctx.Cancelled()


class _Import3D(_Action):

    _known_ext = (
        ".abc",
        ".abcScene",
        ".fbx",
        ".fbxScene",
        ".Unreal",
        ".usda",
        ".usdaScene",
        ".usdc",
        ".usdcScene",
        ".usd",
        ".usdScene",
        ".usdz",
        ".usdzScene",
    )

    def do(self, ctx):
        # type: (_FileContext) -> None
        if not ctx.match_ext(*self._known_ext):
            return

        n = nuke.createNode(
            cast_str("Camera2"),
            cast_str(
                "name Camera_3DEnv_1\n"
                "read_from_file true\n"
                "frame_rate 25\n"
                "suppress_dialog true\n"
                'label "导入的摄像机：\\n\\[basename \\[value file]]"\n'
            ),
        )
        knob_of(
            n,
            "file",
            nuke.File_Knob,
        ).fromUserText(cast_str(ctx.file.raw()))
        if nuke.expression(cast_str("%s.animated" % (cast_text(n.name()),))):
            knob_of(n, "read_from_file", nuke.Boolean_Knob).setValue(False)
        else:
            nuke.delete(n)
            n = nuke.createNode(cast_str("ReadGeo2"))
            knob_of(n, "file", nuke.File_Knob).fromUserText(cast_str(ctx.file.raw()))
            knob_of(n, "all_objects", nuke.Boolean_Knob).setValue(True)
        if n.hasError():
            nuke.delete(n)
            return
        ctx.res.nodes.append(n)


class _ImportNK(_Action):
    def do(self, ctx):
        # type: (_FileContext) -> None
        if not ctx.match_ext(".nk", ".nkc", ".nknc", ".nkind"):
            return
        n = assert_isinstance(
            nuke.nodes.Group(label=cast_str(ctx.file.raw())),
            nuke.Group,
        )
        n.setName(cast_str("Group_import_1"))
        with n:
            nuke.scriptReadFile(cast_str(ctx.file.raw()))
        k = nuke.PyScript_Knob(
            cast_str("expand"),
            cast_str("展开组"),
            cast_str("nuke.thisNode().expand()"),
        )
        n.addKnob(k)
        ctx.res.nodes.append(n)


class _ImportVectorField(_Action):
    def do(self, ctx):
        # type: (_FileContext) -> None
        if not ctx.match_ext(".vf"):
            return
        n = nuke.nodes.Vectorfield(
            vfield_file=cast_str(ctx.file.raw()),
            file_type=cast_str("vf"),
            label=cast_str("[value this.vfield_file]"),
        )
        ctx.res.nodes.append(n)


class _FilenameCheck(_Action):
    def __init__(self):
        self._is_ascii_path_only = None  # type: Optional[bool]

    def is_ascii_path_only(self, ctx):
        # type: (_FileContext) -> bool
        if self._is_ascii_path_only is not None:
            return self._is_ascii_path_only
        self._is_ascii_path_only = nuke.ask(
            cast_str("%s\n使用非英文路径可能导致Nuke出错，全部忽略？" % (ctx.file.name(),)),
        )
        return self._is_ascii_path_only

    def do(self, ctx):
        # type: (_FileContext) -> None

        ignore_pat = (r"thumbs\.db$", r".*\.lock$", r".* - 副本\b")
        basename = os.path.basename(ctx.file.name())
        if basename.startswith("."):
            raise ctx.Cancelled()

        for pat in ignore_pat:
            if re.match(pat, basename, flags=re.I | re.U):
                raise ctx.Cancelled()
        if not is_ascii(ctx.file.name()):
            if self.is_ascii_path_only(ctx):
                raise ctx.Cancelled()

            if ctx.match_ext(".mov", ".mp4"):
                ctx.res.nodes.append(
                    nuke.createNode(
                        cast_str("StickyNote"),
                        cast_str(
                            "autolabel {{'<div align=\"center\">'+autolabel()+'</div>'}} "
                            "label {{{}\n\n"
                            '<span style="color:red;text-align:center;font-weight:bold">'
                            "mov,mp4格式使用非英文路径将可能导致崩溃</span>}}".format(ctx.file.name())
                        ),
                        inpanel=False,
                    )
                )
                raise ctx.Cancelled()


def _should_offset_range(node):
    # type: (nuke.Node) -> bool
    if cast_text(node.Class()) != "Read":
        return False
    first, last = node[cast_str("first")].value(), node[cast_str("last")].value()
    return first != last and first == 1


def _actions():
    yield _FilenameCheck()
    yield _ImportDeepEXR()
    yield _Import3D()
    yield _ImportNK()
    yield _ImportVectorField()
    yield _ImportAny()


def drop_data(mime_type, data):
    # type: (Text, AnyStr) -> Result
    res = Result()
    if mime_type != "text/plain":
        return res
    text = cast_text(data)
    if _should_ignore(text):
        return res
    _LOGGER.debug("will drop: %s %s", mime_type, data)

    actions = tuple(_actions())
    with Progress("处理拖放文件") as p:
        for i in _resolve_file_input(text):
            p.set_message(i)
            p.increase()
            ctx = _FileContext(res, i)
            with ctx:
                for action in actions:
                    action.do(ctx)

        if res.nodes:
            first_frame = nuke.numvalue(cast_str("root.first_frame"))
            if first_frame != 1:
                p.set_message("偏移视频帧范围")
                for n in (i for i in res.nodes if _should_offset_range(i)):
                    assert_isinstance(
                        n[cast_str("frame_mode")],
                        nuke.Enumeration_Knob,
                    ).setValue(cast_str("start_at"))
                    assert_isinstance(
                        n[cast_str("frame")],
                        nuke.String_Knob,
                    ).setValue(cast_str("{:.0f}".format(first_frame)))
            n = res.nodes[0]
            nuke.zoom(
                assert_not_none(nuke.zoom()),
                (n.xpos(), n.ypos()),
            )
    return res


def _on_drop_data(mime_type, data):
    # type: (Text, bytes) -> ...

    try:
        res = drop_data(mime_type, data)
        if res.prevent_default:
            return True
    except:
        _LOGGER.exception("unexpected exception during drop data")
        return True


def init_gui():
    wulifang.nuke.callback.on_drop_data(_on_drop_data)
