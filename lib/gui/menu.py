# -*- coding: UTF-8 -*-
"""Setup UI."""

from __future__ import absolute_import, print_function, unicode_literals


import comp
import comp.panels
import edit
import edit.script_use_seq
import edit.script_use_seq.panels
import nuke
import wulifang.vendor.six as six
from wulifang._util import cast_str, cast_text

WINDOW_CONTEXT = 0
APPLICATION_CONTEXT = 1
DAG_CONTEXT = 2


def add_menu():
    """Add menu for commands and nodes."""

    def _(*args, **kwargs):
        args = (cast_str(i) if isinstance(i, six.text_type) else i for i in args)
        kwargs = tuple(
            {
                k: cast_str(v) if isinstance(v, six.text_type) else v
                for k, v in kwargs.items()
            }.items()
        )
        return (args, kwargs)

    def _auto_comp():
        try:
            comp.Comp().create_nodes()
        except comp.FootageError:
            nuke.message(cast_str("请先导入素材"))

    all_menu = [
        {
            _("工具"): [
                {
                    _("按素材名组装"): [
                        _("对当前工程执行", _auto_comp, icon="autocomp.png"),
                        _(
                            "批量执行",
                            lambda: comp.panels.BatchCompPanel().showModalDialog(),
                            icon="autocomp.png",
                        ),
                        _(
                            "设置",
                            lambda: comp.panels.CompConfigPanel().showModalDialog(),
                            icon="autocomp.png",
                        ),
                    ],
                },
                {
                    _("转换为序列工程"): [
                        _("对当前工程执行", edit.script_use_seq.execute),
                        _(
                            "批量执行",
                            lambda: edit.script_use_seq.panels.BatchPanel().showModalDialog(),
                        ),
                        _(
                            "设置",
                            lambda: edit.script_use_seq.panels.ConfigPanel().showModalDialog(),
                        ),
                    ]
                },
            ]
        }
    ]

    # Add all menu.
    def _add_menu(menu, parent=nuke.menu(cast_str("Nuke"))):
        # type: (..., nuke.Menu) -> None
        assert isinstance(menu, dict)

        for k, v in menu.items():
            m = parent.addMenu(*k[0], **dict(k[1]))
            for i in v:
                if i is None:
                    _ = m.addSeparator()
                elif isinstance(i, dict):
                    _add_menu(i, m)
                elif isinstance(i, tuple):
                    _ = m.addCommand(*i[0], **dict(i[1]))

    for menu in all_menu:
        _add_menu(menu)


def panel_show(keyword):
    """Show control panel for matched nodes."""

    nodes = sorted(
        (
            n
            for n in nuke.allNodes()
            if keyword in n.name()
            and not nuke.numvalue(
                cast_str("%s.disable" % n.name()),
                0,
            )
        ),
        key=lambda n: cast_text(n.name()),
        reverse=True,
    )
    for n in nodes:
        n.showControlPanel()
