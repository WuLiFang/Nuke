# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import argparse
import io
import json
import nuke
import os
import re
import subprocess
import time
import webbrowser
from wulifang._compat.futures import ThreadPoolExecutor

from wulifang._util import (
    cast_str,
    cast_text,
    escape_html,
    iteritems,
    create_html_url,
    alternative_name,
    JSONStorageItem,
    run_in_thread,
    run_in_main_thread,
)
from wulifang.nuke._util import (
    create_knob,
    Panel,
    undoable,
    iter_deep_all_nodes,
    Progress,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Iterable, Iterator, Callable, IO


def dialog(__nodes):
    # type: (Iterable[nuke.Node]) -> None

    _Dialog(__nodes).showModalDialog()


def batch_dialog():
    _BatchDialog().showModalDialog()


_INPUT_DIR = JSONStorageItem(
    "inputDir@873f3fe8-d657-4131-a4c1-a40f51491f11", lambda: ""
)
_OUTPUT_DIR = JSONStorageItem(
    "outputDir@873f3fe8-d657-4131-a4c1-a40f51491f11", lambda: ""
)
_SUBSTITUTE = JSONStorageItem(
    "substitute@873f3fe8-d657-4131-a4c1-a40f51491f11", lambda: "#shot/avi#shot_work#i"
)

_SUBSTITUTE_HELP = "语法为:{分隔符}{查找}{分隔符}{替换}{分隔符}，每个一行。\n支持正则，分隔符后可附选项标志（i: 忽略大小写）。"

_RESULT_ITEM_TYPENAME = "ResultItem_20b600a1e1a7"


class ResultItem:
    def __init__(self, knob_fqn, old_value, new_value, error):
        # type: (Text, Text, Text, Text) -> None
        self.knob_fqn = knob_fqn
        self.old_value = old_value
        self.new_value = new_value
        self.error = error


def _style_html():
    yield """\
<style>
    .list-disc {
        list-style-type: disc;
    }
    .list-decimal {
        list-style-type: decimal;
    }
    .text-error {
        color: red;
    }
    .select-all {
        user-select: all;
    }
    .block {
        display: block;
    }
    .text-green-500 {
        color: #22c55e;
    }
    .font-mono {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    }
    .line-through {
        text-decoration: line-through;
    }
    .text-sm {
        font-size: 0.875rem;
        line-height: 1.25rem;
    }
</style>"""


def _item_html(i):
    # type: (ResultItem) -> ...
    yield "<div>"
    yield "<div>%s" % (i.knob_fqn,)
    if i.error:
        yield """<span class="text-error">%s</span>""" % (i.error,)
    else:
        yield """<span class="text-green-500">OK</span>"""
    yield "</div>"
    yield """\
        <del class="block line-through text-sm"><a class="select-all font-mono" href="com.wlf-studio.open-dir:%s" >%s</a></del>
        <ins class="block text-sm"><a class="select-all font-mono" href="com.wlf-studio.open-dir:%s" >%s</a></ins>
""" % (
        i.old_value,
        i.old_value,
        i.new_value,
        i.new_value,
    )
    yield "</div>"


def _html(result):
    # type: (Iterable[ResultItem]) -> ...
    for i in _style_html():
        yield i
    yield "<h1>替换结果</h1>"
    yield """<ol class="list-disc">"""
    for i in result:
        yield "<li>"
        for j in _item_html(i):
            yield j
        yield "</li>"
    yield "</ol>"


def show(result):
    # type: (Iterable[ResultItem]) -> None

    result = list(result)
    if not result:
        nuke.message(cast_str("没有发现需要替换的文件路径"))
        return

    webbrowser.open(create_html_url("\n".join(_html(result))))


@undoable("替换文件路径")
def replace(__nodes, sub):
    # type: (Iterable[nuke.Node], Callable[[Text],Text]) -> Iterator[ResultItem]
    for n in __nodes:
        for _, k in iteritems(n.knobs()):
            if isinstance(k, nuke.File_Knob):
                for i in replace_knob(k, sub):
                    yield i


def replace_knob(__k, sub):
    # type: (nuke.File_Knob, Callable[[Text],Text]) -> Iterator[ResultItem]
    old_value = cast_text(__k.toScript())
    if not old_value:
        return

    new_value = sub(old_value)
    if old_value == new_value:
        return

    __k.fromScript(cast_str(new_value))
    error = ""
    if not os.path.exists(cast_text(__k.getEvaluatedValue())):
        error = "文件不存在"
    yield ResultItem(
        cast_text(__k.fullyQualifiedName()),
        old_value,
        new_value,
        error,
    )


class _Dialog(Panel):

    def __init__(self, __nodes):
        # type: (Iterable[nuke.Node]) -> None
        Panel.__init__(
            self, cast_str("替换文件路径"), cast_str("com.wlf-studio.replace-path")
        )
        self._nodes = __nodes
        self._knob_sub = create_knob(
            nuke.Multiline_Eval_String_Knob,
            "substitute",
            "替换表达式",
            value=_SUBSTITUTE.get(),
        )
        self.addKnob(self._knob_sub)
        self.addKnob(
            create_knob(
                nuke.Text_Knob,
                "",
                value=_SUBSTITUTE_HELP,
            )
        )

    @property
    def _knob_ok(self):
        return self.knobs().get(cast_str("OK"))

    def knobChanged(self, knob):
        # type: (nuke.Knob) -> None
        if knob is self._knob_sub:
            _SUBSTITUTE.set(cast_text(self._knob_sub.value()))
        elif knob is self._knob_ok:
            self.execute()

    def execute(self):
        try:
            r = _compile_substitute(cast_text(self._knob_sub.value()))
            if r == _noop_replace:
                return

            show(replace(self._nodes, r))
        except Exception as ex:
            nuke.message(cast_str(ex))


class _BatchDialog(Panel):

    def __init__(self):
        # type: () -> None
        Panel.__init__(
            self,
            cast_str("批量替换文件路径"),
            cast_str("com.wlf-studio.batch-replace-path"),
        )

        self._knob_input_dir = create_knob(
            nuke.File_Knob,
            "input_dir",
            label="输入文件夹",
            value=cast_str(_INPUT_DIR.get()),
        )
        self.addKnob(self._knob_input_dir)

        self._knob_output_dir = create_knob(
            nuke.File_Knob,
            "output_dir",
            label="输出文件夹",
            value=cast_str(_OUTPUT_DIR.get()),
        )
        self.addKnob(self._knob_output_dir)

        self._knob_sub = create_knob(
            nuke.Multiline_Eval_String_Knob,
            "substitute",
            "替换表达式",
            value=_SUBSTITUTE.get(),
        )
        self.addKnob(self._knob_sub)
        self.addKnob(
            create_knob(
                nuke.Text_Knob,
                "",
                value=_SUBSTITUTE_HELP,
            )
        )

    @property
    def _knob_ok(self):
        return self.knobs().get(cast_str("OK"))

    def knobChanged(self, knob):
        # type: (nuke.Knob) -> None
        if knob is self._knob_sub:
            _SUBSTITUTE.set(cast_text(self._knob_sub.value()))
        if knob is self._knob_input_dir:
            _INPUT_DIR.set(cast_text(self._knob_input_dir.value()))
        if knob is self._knob_output_dir:
            _OUTPUT_DIR.set(cast_text(self._knob_output_dir.value()))
        elif knob is self._knob_ok:
            self.execute()

    @run_in_thread("replace file path")
    def execute(self):
        try:
            input_dir = cast_text(self._knob_input_dir.value())
            if not input_dir:
                raise ValueError("输入目录为必填")
            output_dir = cast_text(self._knob_output_dir.value())
            if not output_dir:
                raise ValueError("输出目录为必填")
            try:
                os.makedirs(output_dir)
            except OSError:
                pass
            sub = cast_text(self._knob_sub.value())
            r = _compile_substitute(cast_text(sub))
            if r == _noop_replace:
                raise ValueError("替换规则为必填")
            files = [i for i in os.listdir(input_dir) if i.endswith(".nk")]
            if not files:
                raise RuntimeError("在输入目录下没有找到 nk 文件")

            results = []  # type: list[_FileResult]
            with Progress("替换文件路径", estimate_secs=10.0 * len(files)) as p:
                for index, f in enumerate(files):
                    src = os.path.join(input_dir, f)
                    dst = os.path.join(output_dir, f)
                    while os.path.exists(dst):
                        root, ext = os.path.splitext(dst)
                        dst = alternative_name(root) + ext
                    p.set_message("%s (%d/%d)" % (f, index, len(files)))
                    p.increase()

                    proc = subprocess.Popen(
                        (
                            cast_text(nuke.EXE_PATH),
                            "-t",
                            __file__,
                            src,
                            dst,
                            "-s",
                            sub,
                        ),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    assert proc.stdout
                    assert proc.stderr
                    stdout = io.BytesIO()
                    stderr = io.BytesIO()

                    def _copy(r, w):
                        # type: (IO[bytes], IO[bytes]) -> None
                        chunk_size = 1024
                        while True:
                            data = r.read(chunk_size)
                            if w.write(data) < chunk_size:
                                return

                    with ThreadPoolExecutor(2) as pool:
                        pool.submit(_copy, proc.stdout, stdout)  # type: ignore
                        pool.submit(_copy, proc.stderr, stderr)  # type: ignore
                        try:
                            while proc.poll() is None:
                                p.increase()
                                time.sleep(0.1)
                        except Progress.Cancelled:
                            proc.kill()
                            raise
                        results.append(
                            _FileResult(
                                f,
                                cast_text(stdout.getvalue()),
                                cast_text(stderr.getvalue()),
                            )
                        )
            webbrowser.open(create_html_url("\n".join(_batch_result_html(results))))
        except Exception as ex:
            import traceback

            traceback.print_exc()
            run_in_main_thread(nuke.message)(cast_str(ex))


def _batch_result_html(result):
    # type: (Iterable[_FileResult]) -> Iterator[Text]
    for i in _style_html():
        yield i
    yield "<h1>替换结果</h1>"
    yield """<ol class="list-decimal">"""
    for i in result:
        yield "<li>"
        yield "<h2>%s</h2>" % (i.name,)
        # items
        yield """<ol class="list-disc">"""
        for j in i.items():
            yield "<li>"
            for k in _item_html(j):
                yield k
            yield "</li>"
        yield "</ol>"
        # log
        yield "<details>"
        yield "<summary>日志</summary>"
        yield "<h3>stdout</h3>"
        yield "<pre>"
        yield escape_html(i.stdout)
        yield "</pre>"
        yield "<h3>stderr</h3>"
        yield "<pre>"
        yield escape_html(i.stderr)
        yield "</pre>"
        yield "</details>"
        yield "</li>"
    yield "</ol>"


class _FileResult:
    def __init__(self, name, stdout, stderr):
        # type: (Text, Text, Text) -> None
        self.name = name
        self.stdout = stdout
        self.stderr = stderr

    def items(self):
        for i in self.stdout.splitlines():
            if i.startswith("{") and _RESULT_ITEM_TYPENAME in i:
                try:
                    v = json.loads(i)
                    assert v["__typename"] == _RESULT_ITEM_TYPENAME
                    yield ResultItem(
                        v["knobFQN"], v["oldValue"], v["newValue"], v["error"]
                    )
                except:
                    pass


def _compile_substitute(s):
    # type: (Text) -> Callable[[Text], Text]
    replace = _noop_replace

    for i in s.splitlines():
        if not i:
            continue
        sep = i[0]
        values = i.split(sep)[1:]
        if len(values) != 3:
            raise ValueError(
                "替换规则 `%s` 语法错误。首个字母会被识别为分隔符，语法为：{分隔符}{查找}{分隔符}{替换}{分隔符}"
                % (i,)
            )
        flags = 0
        for i in values[2]:
            if i == "i":
                flags |= re.I
            else:
                raise ValueError("不支持的正则标志 `%s`" % (i,))
        pattern = re.compile(values[0], flags)
        repl = values[1]
        previous_replace = replace

        def replace(s):
            # type: (Text) -> Text
            return pattern.sub(repl, previous_replace(s))

    return replace


def _noop_replace(s):
    # type: (Text) -> Text
    return s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="输入文件")
    parser.add_argument("output", help="输出文件")
    parser.add_argument("-s", "--substitute", help="替换规则")
    args = parser.parse_args([cast_text(i) for i in nuke.rawArgs[3:]])

    nuke.scriptReadFile(cast_str(args.input))
    for i in replace(iter_deep_all_nodes(), _compile_substitute(args.substitute)):
        print(
            json.dumps(
                {
                    "__typename": _RESULT_ITEM_TYPENAME,
                    "knobFQN": i.knob_fqn,
                    "oldValue": i.old_value,
                    "newValue": i.new_value,
                    "error": i.error,
                }
            )
        )
    nuke.scriptSaveAs(cast_str(args.output), False)


if __name__ == "__main__":
    main()
