# -*- coding=UTF-8 -*-
"""Shuffle layers.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import re
import webbrowser

import nuke
import nukescripts

from nuketools import undoable_func, utf8
from orgnize import autoplace
from panels import PythonPanel
from wlf.config import Config as BaseConfig


def _shuffle_node_layers_by_re(node, pattern):
    for i in nuke.layers(node):
        if not pattern.search(i):
            continue
        knobs = {
            "inputs": [node],
            "in": i,
            "label": i,
        }
        yield nuke.nodes.Shuffle(**knobs)


def shuffle_layers_by_re(nodes, pattern):
    if isinstance(nodes, nuke.Node):
        nodes = [nodes]
    pattern = re.compile(pattern)
    layers = [j for i in nodes for j in _shuffle_node_layers_by_re(i, pattern)]
    if not layers:
        return []
    return layers + [nuke.nodes.Merge2(
        inputs=layers[:2] + [None] + layers[2:],
        operation='plus',
        label="正则图层分组\n/{}/".format(pattern.pattern).encode("utf8"),
    )]


class Config(BaseConfig):
    default = {
        'pattern': "(?i)_col$\n(?i)_sdw$"
    }
    path = os.path.expanduser(u'~/.nuke/wlf.shuffle_layers_by_re.json')


if nuke.GUI:
    class Panel(PythonPanel):
        def __init__(self):
            super(Panel, self).__init__("正则分离图层组".encode("utf8"))
            self.addKnob(nuke.Multiline_Eval_String_Knob(
                "pattern", "正则匹配规则".encode("utf8")))
            self.addKnob(nuke.Script_Knob("re_help", "正则帮助".encode("utf8")))

            self["re_help"].setFlag(nuke.STARTLINE)
            self["pattern"].setValue(
                Config()["pattern"].encode("utf8"))

        def get_patterns(self):
            return self["pattern"].getValue().splitlines()

        def knobChanged(self, knob):
            if knob is self['re_help']:
                webbrowser.open(
                    "https://docs.python.org/zh-cn/2.7/library/re.html#regular-expression-syntax"
                )

    @undoable_func("正则分离图层组")
    def show_dialog():

        nodes = nuke.selectedNodes()
        if not nodes:
            nuke.message(utf8("请选中要处理的节点"))
            return

        panel = Panel()
        if not panel.showModalDialog():
            return
        Config()["pattern"] = panel["pattern"].getValue()
        patterns = panel.get_patterns()

        created = [
            j
            for i in patterns
            for j in shuffle_layers_by_re(nodes, i)
        ]
        autoplace(created, recursive=True, )
