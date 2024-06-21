# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke
import os
import tempfile
from wulifang.vendor.six.moves import range
from wulifang._util import (
    cast_str,
    cast_text,
    cast_float,
    assert_isinstance,
    JSONStorageItem,
    FileSequence,
)
from wulifang.nuke._util import (
    create_knob,
    Panel,
    undoable,
    Progress,
    create_node,
    knob_of,
    supports_write,
)

import hashlib
import base64
import logging

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Iterable, Optional, Sequence

_LOGGER = logging.getLogger(__name__)


@undoable("生成代理")
def generate(__nodes, scale, out_dir, clear):
    # type: (Sequence[nuke.Node],  float, Text, bool) -> None
    ctx = _Context(
        scale=scale,
        out_dir=out_dir,
        clear=clear,
    )
    read_nodes = list(i for i in __nodes if cast_text(i.Class()) == "Read")
    p = Progress("生成代理")
    for index, i in enumerate(read_nodes):
        p.set_value(index / len(read_nodes))
        p.set_message("%s (%d/%d)" % (cast_text(i.fullName()), index, len(read_nodes)))
        ctx.generate_from_read(i)


def dialog(__nodes):
    # type: (Sequence[nuke.Node]) -> None

    dialog = _Dialog()
    if not dialog.showModalDialog():
        return
    scale = dialog.scale()
    out_dir = dialog.out_dir()
    force = dialog.force()
    try:
        generate(
            __nodes,
            scale,
            out_dir,
            force,
        )
        knob_of(nuke.root(), "proxy", nuke.Boolean_Knob).setValue(True)
        if nuke.numvalue(cast_str("root.proxy_scale"), scale) > scale:
            knob_of(nuke.root(), "proxy_scale", nuke.Array_Knob).setValue(scale)
    except Exception as ex:
        nuke.message(cast_str(ex))


def _default_out_dir():
    # type: () -> Text
    dir = os.getenv("NUKE_TEMP_DIR") or tempfile.tempdir
    if dir:
        return os.path.normpath(dir + "/proxy/")
    return ""


_OUT_DIR = JSONStorageItem(
    "outDir@744ec581-5919-4f69-a1a3-67d569d96152",
    _default_out_dir,
)
_SCALE = JSONStorageItem(
    "scale@744ec581-5919-4f69-a1a3-67d569d96152",
    lambda: nuke.numvalue(cast_str("root.proxy_scale"), 0.5),
)


class _Dialog(Panel):

    def __init__(self):
        # type: () -> None
        Panel.__init__(
            self, cast_str("生成代理"), cast_str("com.wlf-studio.generate-proxy")
        )
        self._knob_out_dir = create_knob(
            nuke.File_Knob,
            "outDir",
            "输出目录",
            value=_OUT_DIR.get(),
            tooltip="代理文件存储目录，输入相对路径时相对于输入文件所在目录。\n"
            "尽量使用高性能的硬盘（比如本地固态）。\n"
            "可手动输出文件以释放存储空间，丢失代理文件再次运行生成即可还原。",
        )
        self.addKnob(self._knob_out_dir)
        self._knob_scale = create_knob(
            nuke.Array_Knob,
            "scale",
            "缩放比例",
            value=_SCALE.get(),
            tooltip="输出文件分辨率缩放比例。\n"
            "如果低于项目的代理缩放比例，会同时更新项目项目设置。",
        )
        self.addKnob(self._knob_scale)
        self._knob_force = create_knob(
            nuke.Boolean_Knob,
            "force",
            "强制重新生成",
            nuke.STARTLINE,
            tooltip="默认不会替换非当前插件生成的代理文件和渲染已有文件，启用此项以强制执行.",
        )
        self.addKnob(self._knob_force)

    def knobChanged(self, knob):
        # type: (nuke.Knob) -> None
        if knob is self._knob_out_dir:
            _OUT_DIR.set(self.out_dir())
        elif knob is self._knob_scale:
            _SCALE.set(self.scale())

    def scale(self):
        return cast_float(self._knob_scale.value())

    def out_dir(self):
        return cast_text(self._knob_out_dir.value())

    def force(self):
        return self._knob_force.value()


class _Context:
    def __init__(self, scale, out_dir, clear):
        # type: (float, Text, bool) -> None
        if scale <= 0:
            raise ValueError("缩放比例必须为正数")
        self._scale = scale
        self._out_dir = out_dir
        self._force = clear

    def _hashed_dir(
        self,
        dir_path,
    ):
        # type: (Text) -> Text
        parent, p = os.path.split(dir_path)
        h = base64.urlsafe_b64encode(
            hashlib.sha256(
                ("wulifang-proxy-file:" + os.path.normpath(parent)).encode("utf-8")
            ).digest()[:6]
        ).decode("ascii")
        return "%s@%s" % (p, h)

    def proxy_path(self, __file):
        # type: (Text) -> Text
        dir, base = os.path.split(__file)
        return os.path.join(dir, self._out_dir, self._hashed_dir(dir), base).replace(
            "\\", "/"
        )

    def is_generated_proxy(self, __file, __proxy):
        # type: (Text, Text) -> bool
        reference = self.proxy_path(__file)
        return os.path.basename(os.path.dirname(reference)) == os.path.basename(
            os.path.dirname(__proxy)
        )

    def generate_from_read(self, __node):
        # type: (nuke.Node) -> Text
        _LOGGER.debug("will generate from read %s", cast_text(__node.fullName()))
        assert cast_text(__node.Class()) == "Read", "unexpected node class '%s'" % (
            __node.Class(),
        )
        file_knob = knob_of(__node, "file", nuke.File_Knob)
        file = cast_text(file_knob.value())
        if not file:
            return ""
        proxy_knob = knob_of(__node, "proxy", nuke.File_Knob)
        proxy = cast_text(proxy_knob.value())
        if proxy and not self._force and not self.is_generated_proxy(file, proxy):
            return proxy
        _, ext = os.path.splitext(file)
        if not supports_write(ext):
            return ""
        # spell-checker: word origfirst origlast
        first_frame = knob_of(__node, "origfirst", nuke.Int_Knob).value()
        last_frame = knob_of(__node, "origlast", nuke.Int_Knob).value()
        proxy = self.proxy_path(file)

        # render
        def render_frames():
            is_sequence = FileSequence.is_sequence(proxy)
            if not is_sequence and os.path.exists(proxy):
                return
            for i in range(
                first_frame,
                last_frame + 1,
            ):
                if (
                    self._force
                    or not is_sequence
                    or not os.path.exists(FileSequence.expand_frame(proxy, i))
                ):
                    yield i

        if any(render_frames()):
            _LOGGER.debug(
                "will render %s from %s %d-%d", proxy, file, first_frame, last_frame
            )
            group = assert_isinstance(
                create_node("Group", name="ProxyRenderer1"), nuke.Group
            )
            try:
                os.makedirs(os.path.dirname(proxy))
            except:
                pass
            with group:
                read = create_node("Read")
                knob_of(read, "file", nuke.File_Knob).fromUserText(
                    cast_str("%s %d-%d" % (file, first_frame, last_frame))
                )
                reformat = create_node(
                    "Reformat",
                    "type scale\n" "filter impulse\n" "scale %s\n" % (self._scale,),
                    inputs=(read,),
                )
                write = create_node(
                    "Write",
                    "channels all\n",
                    inputs=(reformat,),
                )
                knob_of(write, "file", nuke.File_Knob).fromUserText(cast_str(proxy))
                file_type = cast_text(
                    knob_of(write, "file_type", nuke.Enumeration_Knob).value()
                )

                # exr
                # spell-checker: word bitsperchannel
                if file_type == "exr":
                    knob_of(write, "metadata", nuke.Enumeration_Knob).setValue(
                        cast_str("all metadata")
                    )
                    if (
                        cast_text(__node.metadata(cast_str("input/bitsperchannel")))
                        != "16-bit half float"
                    ):
                        knob_of(write, "datatype", nuke.Enumeration_Knob).setValue(
                            cast_str("32 bit float")
                        )
                for start, end in _frame_range_from_ordered_frame(render_frames()):
                    knob_of(nuke.root(), "proxy", nuke.Boolean_Knob).setValue(False)
                    nuke.execute(write, start=start, end=end)

            nuke.delete(group)

        proxy_knob.fromUserText(cast_str("%s %d-%d" % (proxy, first_frame, last_frame)))
        return proxy


def _frame_range_from_ordered_frame(__frames):
    # type: (Iterable[int]) -> Iterable[tuple[int, int]]
    start = None  # type: Optional[int]
    previous = None  # type: Optional[int]
    for i in __frames:
        if start is None or previous is None:
            start = i
            previous = i
            continue
        if i <= previous:
            raise ValueError("only supports ordered input")
        if i != previous + 1:
            yield (start, i)
            start = i + 1
        previous = i
    if start is not None and previous is not None and start <= previous:
        yield (start, previous)
