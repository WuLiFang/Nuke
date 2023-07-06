# -*- coding=UTF-8 -*-
"""Panels for `cgtwn`.  """

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke

from wulifang.vendor import cgtwq
from wulifang.vendor.cgtwq import core
import wulifang
from wulifang._util import cast_str, cast_text


def dialog_login():
    """Login teamwork."""

    client = cgtwq.DesktopClient()
    if client.is_logged_in():
        client.connect()
        wulifang.message.info("登录成功", title="CGTeamWork")
        return
    account = "帐号"
    password = "密码"
    panel = nuke.Panel(cast_str(""))
    _ = panel.addSingleLineInput(cast_str(account), cast_str(""))
    _ = panel.addPasswordInput(cast_str(password), cast_str(""))

    while True:
        confirm = panel.show()
        if confirm:
            try:
                core.CONFIG["DEFAULT_TOKEN"] = cgtwq.login(
                    cast_text(panel.value(cast_str(account)) or ""),
                    cast_text(panel.value(cast_str(password)) or ""),
                ).token
            except ValueError:
                wulifang.message.info("登录失败", title="CGTeamWork")
                continue
            wulifang.message.info("登录成功", title="CGTeamWork")
        break
