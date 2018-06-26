# -*- coding=UTF-8 -*-
"""Panels for `cgtwn`.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import os
import webbrowser

import nuke

import cgtwq
from nuketools import utf8
from wlf.progress import CancelledError, progress
from wlf.uitools import Tray

LOGGER = logging.getLogger(__name__)


def dialog_login():
    """Login teamwork.  """

    if cgtwq.DesktopClient.is_logged_in():
        cgtwq.update_setting()
        Tray.message('CGTeamWork', '登录成功')
        return
    account = '帐号'
    password = '密码'
    panel = nuke.Panel(utf8('登录CGTeamWork'))
    panel.addSingleLineInput(utf8('帐号'), '')
    panel.addPasswordInput(utf8('密码'), '')

    while True:
        confirm = panel.show()
        if confirm:
            try:
                cgtwq.server.setting.DEFAULT_TOKEN = cgtwq.login(
                    panel.value(account), panel.value(password))
            except ValueError:
                Tray.message('CGTeamWork', '登录失败')
                continue
            Tray.message('CGTeamWork', '登录成功')
        break


def dialog_create_dirs():
    """A dialog for create dirs from cgtwq.  """

    folder_input_name = b'输出文件夹'
    database_input_name = b'数据库'
    prefix_input_name = b'镜头名前缀限制'
    panel = nuke.Panel(b'为项目创建文件夹')
    panel.addSingleLineInput(database_input_name, 'proj_qqfc_2017')
    panel.addSingleLineInput(prefix_input_name, '')
    panel.addFilenameSearch(folder_input_name, 'E:/temp')
    confirm = panel.show()
    if not confirm:
        return

    try:
        database = panel.value(database_input_name)
        save_path = panel.value(folder_input_name)
        prefix = panel.value(prefix_input_name)

        for _ in progress(['连接CGTeamWork...', ], '创建文件夹'):
            try:
                select = cgtwq.Database(database)['shot_task'].filter(
                    cgtwq.Field('pipeline') == '合成')
            except cgtwq.IDError as ex:
                nuke.message(utf8('找不到对应条目\n{}'.format(ex)))
                return

        for name in progress(select['shot.shot'], '创建文件夹'):
            if not name or not name.startswith(prefix):
                continue
            _path = os.path.join(save_path, name)
            if not os.path.exists(_path):
                os.makedirs(_path)
        webbrowser.open(save_path)
    except CancelledError:
        LOGGER.debug('用户取消创建文件夹')
