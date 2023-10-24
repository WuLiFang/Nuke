# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Iterable, Optional, Iterator

import nuke

from wulifang.nuke._util import knob_of
from wulifang._util import cast_str, cast_text, create_html_url
import wulifang.nuke
import webbrowser
from ._cryptomatte_list import CryptomatteList
from ._cryptomatte_manifest import CryptomatteManifest


class ResultItem:
    def __init__(self, node):
        # type: ( nuke.Node) -> None
        self.node_name = cast_text(node.fullName())
        self.logs = []  # type: list[Text]
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


def _one_way_match_score(a, b):
    # type: (Text,Text) -> float
    if a == b:
        return 1

    if len(a) < 2:
        return 0.2

    if a.endswith(b):
        return 0.9
    if a.startswith(b):
        return 0.8
    if a in b:
        return 0.7

    return 0


def _match_score(a, b):
    # type: (Text,Text) -> float
    return max(_one_way_match_score(a, b), _one_way_match_score(b, a))


def fix(nodes):
    # type: (Iterable[nuke.Node]) -> Iterator[ResultItem]

    for n in nodes:
        if (
            cast_text(n.Class()) not in ("Cryptomatte")
            or knob_of(n, "disable", nuke.Boolean_Knob).value()
        ):
            continue

        ctx = _Context(n)
        try:
            _, manifest = CryptomatteManifest.from_cryptomatte(n)
        except ValueError:
            ctx.log("无法获取清单")
            continue

        l = CryptomatteList.from_cryptomatte(n)
        if l.has_wildcard():
            ctx.log("暂不支持通配符")
            continue

        used_name = set(l.raw)
        new_value = list()  # type: list[str]
        lost_count = 0
        for i in l.raw:
            if i in manifest.raw:
                new_value.append(i)
                continue
            lost_count += 1
            matches = (
                (j, _match_score(i, j)) for j in manifest.raw if j not in used_name
            )
            matches = sorted((k for k in matches if k[1] > 0), key=lambda x: x[1])
            if not matches:
                ctx.log("名称不存在于清单中，无法找到匹配: %s" % (i,))
                new_value.append(i)
                continue
            best_match, score = matches[0]
            ctx.log(
                "名称不存在于清单中，替换为最佳匹配(评分 %.2f):\n\t%s\n->\t%s" % (score, i, best_match)
            )
            new_value.append(best_match)
            used_name.add(best_match)
            ctx.res.ok = True
        if lost_count == 0:
            continue
        if ctx.res.ok:
            CryptomatteList(new_value).to_cryptomatte(n)
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
