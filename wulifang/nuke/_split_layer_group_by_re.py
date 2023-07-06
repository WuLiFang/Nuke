# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Union, Iterable, Iterator, Sequence


import os
import re
import webbrowser
import json
import codecs
import nuke

from wulifang._util import (
    cast_str,
    cast_text,
    cast_iterable,
    force_rename,
    JSONStorageItem,
    workspace_path,
)
from wulifang.nuke._util import (
    Panel as _Panel,
    create_node,
    undoable,
)
from wulifang.nuke._auto_place import auto_place


def _split_one(node, pattern):
    # type: (nuke.Node, re.Pattern[Text]) -> Iterator[nuke.Node]
    for layer_str in nuke.layers(node):
        layer = cast_text(layer_str)
        if not pattern.search(layer):
            continue
        yield create_node(
            "Shuffle",
            "in %s" % (layer,),
            inputs=(node,),
            label=layer,
        )


def split(nodes, pattern):
    # type: (Union[nuke.Node, Iterable[nuke.Node]], re.Pattern[Text]) -> Sequence[nuke.Node]
    pattern = re.compile(pattern)
    layers = [j for i in cast_iterable(nodes) for j in _split_one(i, pattern)]
    if not layers:
        return []
    return layers + [
        create_node(
            "Merge2",
            "operation plus",
            inputs=layers[:2] + [None] + layers[2:],
            label="正则图层分组\n/%s/" % (pattern.pattern,),
        ),
    ]


def _migrate_legacy_config():
    p = os.path.expanduser("~/.nuke/wlf.shuffle_layers_by_re.json")
    if os.path.exists(p):
        with codecs.open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "pattern" in data:
                _PATTERN.set(data["pattern"])
        force_rename(p, p + "~")


_PATTERN = JSONStorageItem(
    "pattern@48017c27-ad7d-453a-bee4-383d49122bf6",
    lambda: "(?i)_col$\n(?i)_sdw$",
)


class Panel(_Panel):
    def __init__(self):
        super(Panel, self).__init__(cast_str("正则分离图层组"))
        self.addKnob(
            nuke.Script_Knob(
                cast_str("help"),
                cast_str("查看帮助文档"),
            )
        )
        self.pattern_knob = nuke.Multiline_Eval_String_Knob(
            cast_str("pattern"),
            cast_str("正则匹配规则"),
        )
        self.addKnob(self.pattern_knob)

        self.pattern_knob.setValue(cast_str(_PATTERN.get()))

    def knobChanged(self, knob):
        # type: (nuke.Knob) -> None
        if knob is self["help"]:
            webbrowser.open(
                workspace_path("docs/_build/html/features/split_layer_group_by_re.html")
            )


@undoable("正则分离图层组")
def dialog(_nodes):
    # type: (Iterable[nuke.Node]) -> None
    _migrate_legacy_config()
    panel = Panel()
    if not panel.showModalDialog():
        return
    raw_pattern = cast_text(panel.pattern_knob.value())
    _PATTERN.set(raw_pattern)

    raw_patterns = [i for i in raw_pattern.splitlines() if i]
    auto_place_nodes = []  # type: list[nuke.Node]
    for n in _nodes:
        for raw_pattern in raw_patterns:
            if not raw_pattern:
                return
            try:
                pattern = re.compile(raw_pattern)
                auto_place_nodes.extend(split(n, pattern))
            except re.error:
                pass
        auto_place_nodes.append(n)
    auto_place(auto_place_nodes)
