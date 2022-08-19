# -*- coding=UTF-8 -*-
"""Panels for `cgtwn`.  """

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke

from wulifang.vendor import cgtwq
from wulifang.vendor.cgtwq import core
import wulifang
import wulifang.vendor.cast_unknown as cast


def dialog_login():
    """Login teamwork."""

    client = cgtwq.DesktopClient()
    if client.is_logged_in():
        client.connect()
        wulifang.message.info("登录成功", title="CGTeamWork")
        return
    account = "帐号"
    password = "密码"
    panel = nuke.Panel(b"")
    _ = panel.addSingleLineInput(cast.binary(account), b"")
    _ = panel.addPasswordInput(cast.binary(password), b"")

    while True:
        confirm = panel.show()
        if confirm:
            try:
                core.CONFIG["DEFAULT_TOKEN"] = cgtwq.login(
                    panel.value(cast.binary(account)) or "",
                    panel.value(cast.binary(password)) or "",
                ).token
            except ValueError:
                wulifang.message.info("登录失败", title="CGTeamWork")
                continue
            wulifang.message.info("登录成功", title="CGTeamWork")
        break
