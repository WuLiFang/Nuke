# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Iterable, Optional, Iterator

import nuke
import json

from wulifang.nuke._util import knob_of, Progress
from wulifang._util import cast_str, cast_text, create_html_url
from wulifang.vendor.six.moves import range
import wulifang.nuke
import webbrowser
from ._cryptomatte_list import CryptomatteList
from ._cryptomatte_manifest import CryptomatteManifest
import re


class ResultItem:
    def __init__(self, node):
        # type: ( nuke.Node) -> None
        self.node_name = cast_text(node.fullName())
        self.logs = []  # type: list[Text]
        self.manifest = None  # type: Optional[CryptomatteManifest]
        self.ok = False


class _Context:
    class Done(RuntimeError):
        def __init__(self):
            RuntimeError.__init__(self, "done")

    def __init__(self, node):
        # type: (nuke.Node) -> None
        self.node = node
        self.filename = cast_text(nuke.filename(node) or "")
        self.res = ResultItem(node)

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


class _NameMatcher:
    _SEPARATOR_PATTERN = re.compile(r"[:\/]")
    _MAX_LEN = 16 << 10

    def __init__(self, a, b):
        # type: (Text, Text) -> None
        if len(a) > len(b):
            a, b = b, a
        if len(b) > self._MAX_LEN:
            raise ValueError("name is too long (length=%d)" % (len(b),))
        self.a = a
        self.b = b

    def _common_prefix(self, a, b):
        # type: (Text,Text) -> Text
        for index in range(len(a)):
            if a[index] != b[index]:
                return a[:index]
        return a

    def _common_suffix(self, a, b):
        # type: (Text,Text) -> Text
        for index in range(len(a)):
            if a[len(a) - 1 - index] != b[len(b) - 1 - index]:
                return a[len(a) - index :]
        return a

    def _base_score(self, a, b):
        # type: (Text, Text) -> tuple[float, Text]
        if a == b:
            return 1, "相同"

        if len(a) > len(b):
            a, b = b, a

        if len(a) < 2:
            return 0.01 * len(a) / self._MAX_LEN, "输入过短"

        common_suffix = self._common_suffix(a, b)
        if len(common_suffix) > len(a) / 2:
            return 0.6 + 0.09 * len(common_suffix) / len(a) + 0.01 * len(
                a
            ) / self._MAX_LEN, "共通后缀 '%s'" % (common_suffix,)

        if not self._SEPARATOR_PATTERN.match(a):
            common_prefix = self._common_prefix(a, b)
            if len(common_prefix) > len(a) / 2:
                return 0.4 + 0.09 * len(common_prefix) / len(a) + 0.01 * len(
                    a
                ) / self._MAX_LEN, "共通前缀 '%s'" % (common_prefix,)

        if a in b:
            return 0.3 + 0.09 * len(a) / len(b) + 0.01 * len(
                a
            ) / self._MAX_LEN, "包含 '%s'" % (a,)

        return 0, "不匹配"

    def _solutions(self):
        yield self._base_score(self.a, self.b)
        a_parts = self._SEPARATOR_PATTERN.split(self.a)
        if len(a_parts) > 1:
            b_parts = self._SEPARATOR_PATTERN.split(self.b)
            score, comment = self._base_score(a_parts[-1], b_parts[-1])
            if score > 0.5:
                yield score * 0.8, "最后一部分:" + comment

    def score(self):
        # type: () -> tuple[float, Text]

        solutions = sorted(self._solutions(), key=lambda x: x[0], reverse=True)
        return solutions[0]


class _MatchContext:
    def __init__(self, parent, manifest, list):
        # type: (_Context, CryptomatteManifest, CryptomatteList) -> None
        self.parent = parent
        self.manifest = manifest
        self.list = list
        self.used_name = set(list.raw)  # type: set[str]


class _Layer:
    def __init__(self, ctx, name):
        # type: ( _MatchContext, Text) -> None
        self.ctx = ctx
        self.name = name
        self.name_fixed = name
        self.did_fix = name in ctx.manifest.raw
        self._raw_matches = tuple(
            (j, _NameMatcher(self.name, j).score()) for j in self.ctx.manifest.raw
        )

    def _matches(self):
        for i, score in self._raw_matches:
            if i in self.ctx.used_name:
                continue
            if score[0] > 0:
                yield score[0], i, score[1]

    def best_match(self):
        matches = sorted(self._matches(), reverse=True)
        if matches:
            return matches[0]

    def fix(self):
        if self.did_fix:
            return
        self.did_fix = True
        match = self.best_match()
        if not match:
            self.ctx.parent.log("无法找到匹配:\n\t%s" % (self.name,))
            return
        score, name, explain = match
        self.name_fixed = name
        self.ctx.used_name.add(name)
        self.ctx.parent.log(
            "替换为最佳匹配:\n\t评分 %.2f\t%s\n\t\t%s\n\t->\t%s"
            % (score, explain, self.name, self.name_fixed)
        )
        self.ctx.parent.res.ok = True


def fix(nodes):
    # type: (Iterable[nuke.Node]) -> Iterator[ResultItem]
    with Progress("修复 Cryptomatte 名称丢失", estimate_secs=120) as p:
        for n in nodes:
            if (
                cast_text(n.Class()) not in ("Cryptomatte")
                or knob_of(n, "disable", nuke.Boolean_Knob).value()
            ):
                continue
            p.set_message(cast_text(n.fullName()))
            p.increase()

            ctx = _Context(n)
            try:
                _, manifest = CryptomatteManifest.from_cryptomatte(n)
                ctx.res.manifest = manifest
            except ValueError:
                ctx.log("无法获取清单")
                yield ctx.res
                continue

            l = CryptomatteList.from_cryptomatte(n)
            if l.has_wildcard():
                ctx.log("暂不支持通配符")
                yield ctx.res
                continue

            m_ctx = _MatchContext(ctx, manifest, l)
            layers = [_Layer(m_ctx, i) for i in l.raw]
            did_fix = False
            while True:
                remains = sorted(
                    (i for i in layers if not i.did_fix),
                    key=lambda x: x.best_match() or (-1,),
                    reverse=True,
                )
                if not remains:
                    break
                remains[0].fix()
                did_fix = True

            if not did_fix:
                continue

            if ctx.res.ok:
                CryptomatteList([i.name_fixed for i in layers]).to_cryptomatte(n)
            yield ctx.res


def _html(items):
    # type: (list[ResultItem]) -> Iterator[Text]
    yield "<!DOCTYPE html>"
    yield '<html lang="zh-Hans">'
    yield "<head>"
    yield "<title>修复结果</title>"
    yield "</head>"
    yield "<body>"
    yield "<h1>修复结果</h1>"
    yield "<div>%d 成功, %d 失败</div>" % (
        sum(i.ok for i in items),
        sum(not i.ok for i in items),
    )
    yield "<ul>"
    for i in items:
        yield "<li>"
        yield "[%s]%s " % ("成功" if i.ok else "失败", i.node_name)
        if i.manifest:
            yield """<details><summary style="
    position: sticky;
    top: 0;
    background: white;
">清单</summary><pre>%s</pre></details>""" % (
                json.dumps(i.manifest.raw, ensure_ascii=False, indent=2)
            )
        for j in i.logs:
            yield """<pre style="margin: 5px 20px;">%s</pre>""" % (j,)
        yield "</li>"
    yield "</ul>"
    yield "</body>"
    yield "</html>"


def show(items, verbose=False):
    # type: (Iterable[ResultItem], bool) -> None
    items = list(items)
    if not items:
        if verbose:
            nuke.message(cast_str("没有需要修复的节点"))
        return

    html = "\n".join(_html(items))
    webbrowser.open(create_html_url(html))


def _on_cryptomatte_create():
    n = nuke.thisNode()
    l = CryptomatteList.from_cryptomatte(n)
    if l.has_wildcard():
        return
    try:
        _, manifest = CryptomatteManifest.from_cryptomatte(n)
    except ValueError:
        return

    for i in l.raw:
        if i not in manifest.raw:
            wulifang.message.info(
                "检测到 %s.matteList 中使用了未知的名称(%s)，建议尝试 `编辑` - `Cryptomatte: 修复名称丢失` 功能"
                % (
                    cast_text(nuke.thisNode().fullName()),
                    i,
                )
            )
            return


def init_gui():
    wulifang.nuke.callback.on_create(_on_cryptomatte_create, node_class="Cryptomatte")
