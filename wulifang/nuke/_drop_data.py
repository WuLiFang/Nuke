# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import re
import logging
import mimetypes

import nuke

import wulifang.nuke
from wulifang._util import (
    cast_text,
    cast_str,
    assert_isinstance,
    is_ascii,
    assert_not_none,
)
from wulifang.nuke._util import (
    Progress,
    knob_of,
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


def _resolve_filename_by_path(path):
    # type: (Text) -> Iterator[Text]
    if os.path.isdir(path):
        for dirpath, _, _ in os.walk(path):
            dirpath = dirpath.replace("\\", "/")
            for i in nuke.getFileNameList(cast_str(dirpath)):
                yield "{}/{}".format(dirpath, cast_text(i))
    else:
        yield path


def _resolve_filename(data):
    # type: (Text) -> Iterator[Text]

    url = urllib_parse.urlparse(data)
    if url.scheme == "file":
        for i in _resolve_filename_by_path(urllib_parse.unquote(url.path)):
            yield i
    else:
        for i in _resolve_filename_by_path(data):
            yield i


class Result:
    nodes = []  # type: list[nuke.Node]
    prevent_default = False


class _FileContext:
    class Cancelled(RuntimeError):
        def __init__(self):
            RuntimeError.__init__(self, "cancelled")

    def __init__(self, res, filename):
        # type: (Result,Text) -> None
        self.res = res
        self.filename = filename
        _, ext = os.path.splitext(self.filename)
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
            cast_str(ctx.filename)
        )
        if n.hasError():
            nuke.delete(n)
            return
        ctx.res.nodes.append(n)


class _ImportAny(_Action):
    # powershell under NukeX.YvZ/plugins:
    # > ls *Reader.dll | % { $_.Name -replace '(.*)Reader.dll','.$1' }
    _known_ext = (
        # ".abc",
        ".arri",
        ".avi",
        ".cin",
        ".crw",
        ".dng",
        ".dpx",
        ".exr",
        # ".fbx",
        ".fpi",
        ".gif",
        ".hdr",
        ".iff",
        ".jpeg",
        # ".mov32",
        # ".mov64",
        ".mov",
        ".mxf",
        # ".nkc",
        # ".nk",
        ".obj",
        ".pic",
        ".png",
        ".psd",
        ".r3d",
        ".rla",
        ".sgi",
        ".targa",
        ".tiff",
        ".xpm",
        ".yuv",
    )

    def do(self, ctx):
        # type: (_FileContext) -> None
        if not ctx.match_ext(*self._known_ext):
            mime, _ = mimetypes.guess_type(ctx.filename)
            if not (mime and mime.startswith(("image/", "video/"))):
                ctx.res.nodes.append(
                    create_node(
                        "StickyNote",
                        label="未支持导入此文件类型（%s）:\n%s" % (mime, ctx.filename),
                    )
                )
                return

        n = nuke.createNode(cast_str("Read"))

        assert_isinstance(n[cast_str("file")], nuke.File_Knob).fromUserText(
            cast_str(ctx.filename)
        )
        if n.hasError():
            nuke.delete(n)
            return
        ctx.res.nodes.append(n)
        raise ctx.Cancelled()


class _Import3D(_Action):
    def do(self, ctx):
        # type: (_FileContext) -> None
        if not ctx.match_ext(".fbx", ".abc"):
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
        ).fromUserText(cast_str(ctx.filename))
        if nuke.expression(cast_str("%s.animated" % (cast_text(n.name()),))):
            knob_of(n, "read_from_file", nuke.Boolean_Knob).setValue(False)
        else:
            nuke.delete(n)
            n = nuke.createNode(cast_str("ReadGeo2"))
            knob_of(n, "file", nuke.File_Knob).fromUserText(cast_str(ctx.filename))
            knob_of(n, "all_objects", nuke.Boolean_Knob).setValue(True)
        if n.hasError():
            nuke.delete(n)
            return
        ctx.res.nodes.append(n)


class _ImportNK(_Action):
    def do(self, ctx):
        # type: (_FileContext) -> None
        if not ctx.match_ext(".nk", ".nkc"):
            return
        n = assert_isinstance(
            nuke.nodes.Group(label=cast_str(ctx.filename)),
            nuke.Group,
        )
        n.setName(cast_str("Group_import_1"))
        with n:
            nuke.scriptReadFile(cast_str(ctx.filename))
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
            vfield_file=cast_str(ctx.filename),
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
            cast_str("%s\n使用非英文路径可能导致Nuke出错，全部忽略？" % (ctx.filename,)),
        )
        return self._is_ascii_path_only

    def do(self, ctx):
        # type: (_FileContext) -> None

        ignore_pat = (r"thumbs\.db$", r".*\.lock$", r".* - 副本\b")
        basename = os.path.basename(ctx.filename)
        if basename.startswith("."):
            raise ctx.Cancelled()

        for pat in ignore_pat:
            if re.match(pat, basename, flags=re.I | re.U):
                raise ctx.Cancelled()
        if not is_ascii(ctx.filename):
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
                            "mov,mp4格式使用非英文路径将可能导致崩溃</span>}}".format(ctx.filename)
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
        for i in _resolve_filename(text):
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
                print(res.nodes)
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
