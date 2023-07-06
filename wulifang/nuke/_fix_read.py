# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import webbrowser

import nuke

from wulifang._util import cast_str, cast_text, FileSequence, create_html_url
from wulifang.nuke._util import knob_of
from ._drop_data import drop_data

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Protocol, Iterable, Iterator, Optional

    class _Fix(Protocol):
        def do(self, ctx):
            # type: (_Context) -> None
            pass

else:
    _Fix = object


_LOGGER = logging.getLogger(__name__)


def _set_filename(n, value):
    # type: (nuke.Node, Text) -> None
    k = knob_of(n, "file", nuke.File_Knob)
    try:
        proxy = knob_of(n, "proxy", nuke.File_Knob)
        if cast_text(nuke.value(cast_str("root.proxy"))) == "true" and proxy.value():
            k = proxy
    except NameError:
        pass
    k.setValue(cast_str(value))


class _CurrentFiles:
    def __init__(self):
        filenames = set(
            cast_text(nuke.filename(n) or "")
            for n in nuke.allNodes()
            if not n.hasError()
        )
        frame = nuke.frame()
        self._by_basename = {
            os.path.basename(
                FileSequence.expand_frame(i, frame),
            ): i
            for i in filenames
        }

    def get_by_basename(self, basename):
        # type: (Text) -> Text
        return self._by_basename.get(basename, "")


class ResultItem:
    def __init__(self, node):
        # type: ( nuke.Node) -> None
        self.node_name = cast_text(node.name())
        self.logs = []  # type: list[Text]
        self.ok = False


class _Context:
    class Done(RuntimeError):
        def __init__(self):
            RuntimeError.__init__(self, "done")

    def __init__(self, files, node):
        # type: ( _CurrentFiles,nuke.Node) -> None
        self.files = files
        self.node = node
        self.filename = cast_text(nuke.filename(node) or "")
        self.res = ResultItem(node)

    def current_basename(self):
        return os.path.basename(FileSequence.expand_frame(self.filename, nuke.frame()))

    def log(self, msg):
        # type: (Text) -> None
        self.res.logs.append(msg)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # type: (Optional[type], Optional[Exception], Optional[object]) -> bool

        if exc_type is _Context.Done:
            self.res.ok = True
            return True
        return False


class _RemoveThumbsDB(_Fix):
    def do(self, ctx):
        # type: (_Context) -> None
        if os.path.basename(ctx.filename).lower() != "thumbs.db":
            return
        ctx.log("thumbs.db 不会是素材文件，自动删除")
        nuke.delete(ctx.node)
        raise ctx.Done()


class _ReplaceMissingFile(_Fix):
    def do(self, ctx):
        # type: (_Context) -> None
        match = ctx.files.get_by_basename(ctx.current_basename())
        if match:
            _set_filename(ctx.node, match)
            if ctx.node.hasError():
                ctx.log("使用新素材依旧出错, 撤销替换: %s" % (match,))
                _set_filename(ctx.node, ctx.filename)
                return

            ctx.log(
                "使用同名文件: %s" % (match,),
            )
            raise ctx.Done()
        ctx.log("找不到可替换的素材")


class _ExpandDir(_Fix):
    def do(self, ctx):
        # type: (_Context) -> None
        if not os.path.isdir(ctx.filename):
            return

        res = drop_data("text/plain", ctx.filename)
        if res.nodes:
            ctx.log("展开文件夹")
            nuke.delete(ctx.node)
            raise ctx.Done()


_FIXES = (
    _RemoveThumbsDB(),
    _ExpandDir(),
    _ReplaceMissingFile(),
)


def fix(nodes):
    # type: (Iterable[nuke.Node]) -> Iterator[ResultItem]

    files = _CurrentFiles()
    for n in nodes:
        if (
            cast_text(n.Class()) not in ("Read", "DeepRead")
            or not n.hasError()
            or knob_of(n, "disable", nuke.Boolean_Knob).value()
        ):
            continue
        ctx = _Context(files, n)
        with ctx:
            for fix in _FIXES:
                fix.do(ctx)
        yield ctx.res


def _html(items):
    # type: (list[ResultItem]) -> Iterator[Text]
    yield "<h1>修复结果</h1>"
    yield "<div>%d 成功, %d 失败</div>" % (
        sum(i.ok for i in items),
        sum(not i.ok for i in items),
    )
    yield "<ul>"
    for i in items:
        yield "<li>"
        yield "[%s]%s " % ("成功" if i.ok else "失败", i.node_name)
        if i.logs:
            yield """<pre style="margin: 0 20px;">%s</pre>""" % ("\n".join(i.logs),)
        yield "</li>"
    yield "</ul>"


def show(items, verbose=False):
    # type: (Iterable[ResultItem], bool) -> None
    items = list(items)
    if not items:
        if verbose:
            nuke.message(cast_str("没有需要修复的节点"))
        return

    html = "\n".join(_html(items))
    webbrowser.open(create_html_url(html))
