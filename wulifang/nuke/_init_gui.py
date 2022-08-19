# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals
from wulifang.nuke.infrastructure.autolabel_service import AutolabelService

import wulifang
from wulifang.nuke.infrastructure import pyblish
from wulifang.vendor import cgtwq
import nuke
import wulifang.nuke


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


def init_gui():
    if _g.init_once:
        return
    nuke.menu("Nuke".encode("utf-8")).addMenu("帮助".encode("utf-8")).addCommand(
        "重新加载吾立方插件".encode("utf-8"),
        _reload,
        "Ctrl+Shift+F5".encode("utf-8"),
    )
    wulifang.publish = pyblish.PublishService()

    autolabel = AutolabelService(wulifang.file)
    wulifang.nuke.cleanup.add(lambda: nuke.removeAutolabel(autolabel.autolabel))
    nuke.addAutolabel(autolabel.autolabel)

    _init_cgtw()
    _g.init_once = True
