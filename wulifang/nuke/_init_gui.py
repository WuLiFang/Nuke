# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text

import wulifang
import wulifang.license
import wulifang.nuke
from wulifang.nuke.infrastructure import pyblish
from wulifang.nuke.infrastructure.autolabel_service import AutolabelService
from wulifang.vendor import cgtwq

import nuke

from ._init import skip_gui as _skip
from ._pack_project import pack_project
from . import _preference, _project_settings


def _reload():
    import wulifang.nuke

    wulifang.nuke.reload()


def _init_cgtw():

    client = cgtwq.DesktopClient()
    if not client.executable():
        return

    import time

    started = time.time()
    while time.time() - started < 10:
        try:
            client.start()
            wulifang.nuke.callback.on_script_load(lambda: client.connect())
            nuke.addOnScriptLoad
            if client.is_logged_in():
                client.connect()
            break
        except:
            import traceback

            traceback.print_exc()


class _g:
    init_once = False


def _obtain_menu(parent, name):
    # type: (nuke.Menu, Text) -> nuke.Menu
    name_b = name.encode("utf-8")
    return parent.menu(name_b) or parent.addMenu(name_b)


def _init_menu():
    rootMenu = nuke.menu("Nuke".encode("utf-8"))

    rootMenu.addMenu("帮助".encode("utf-8")).addCommand(
        "重新加载吾立方插件".encode("utf-8"),
        _reload,
        "Ctrl+Shift+F5".encode("utf-8"),
    )
    editMenu = _obtain_menu(rootMenu, "编辑")
    editMenu.addCommand(
        "打包工程".encode("utf-8"),
        pack_project,
    )


def init_gui():
    if _g.init_once or _skip():
        return
    wulifang.publish = pyblish.PublishService()
    autolabel = AutolabelService(wulifang.file)
    wulifang.cleanup.add(lambda: nuke.removeAutolabel(autolabel.autolabel))

    nuke.addAutolabel(autolabel.autolabel)
    _init_menu()
    _project_settings.init()
    _preference.init_gui()
    _init_cgtw()
    _g.init_once = True
