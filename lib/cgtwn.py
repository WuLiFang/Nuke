# -*- coding=UTF-8 -*-
"""
cgteamwork integration for nuke.
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import webbrowser

import nuke

from edit import CurrentViewer
from nuketools import utf8
import cgtwq
from wlf.notify import CancelledError, progress, traytip
from wlf.path import Path

LOGGER = logging.getLogger('com.wlf.cgtwn')


class Database(cgtwq.Database):
    """Optimized cgtwq database fro nuke.   """

    @classmethod
    def from_shot(cls, shot, default=None):
        """Get database from filename.

        Args:
            shot (unicode): shot name to get database.
            default (unicode, optional): Defaults to None.
                Default database name.

        Raises:
            ValueError: When no matched database,
                and `default` is not set.

        Returns:
            Database: Filename related database.
        """

        data = cgtwq.PROJECT.all().get_fields('code', 'database')
        for i in data:
            code, database = i
            if unicode(shot).startswith(code):
                return cls(database)
        if default:
            return cls(default)
        raise ValueError(
            'Can not determinate database from filename.', shot)


class Task(cgtwq.Entry):
    """Selection for single shot.  """
    # pylint: disable=too-many-ancestors

    shot = None

    def __unicode__(self):
        database = self.module.database
        project = cgtwq.PROJECT.filter(cgtwq.Filter(
            'database', database.name))['full_name'][0]
        return '{}: {}'.format(project, self.shot)

    def import_video(self, sign):
        """Import corresponse video by filebox sign.

        Args:
            sign (unicode): Server defined fileboxsign

        Returns:
            nuke.Node: Created read node.
        """

        node_name = {'animation_videos': '动画视频'}.get(sign, sign)
        n = nuke.toNode(utf8(node_name))
        if n is None:
            dir_ = self.get_filebox(sign).path
            videos = Path(dir_).glob('{}.*'.format(self.shot))
            for video in videos:
                n = nuke.nodes.Read(name=utf8(node_name))
                n['file'].fromUserText(unicode(video).encode('utf-8'))
                break
        n['frame_mode'].setValue(b'start_at')
        n['frame'].setValue(b'{:.0f}'.format(
            nuke.numvalue('root.first_frame')))
        CurrentViewer().link(n, 4, replace=False)
        return n

    @classmethod
    def from_shot(cls, shot, pipeline='合成'):
        """Get task entry from shot name.

        Args:
        shot (str): Shot name.
            pipeline (str, optional): Defaults to '合成'. Pipline name.
        """
        database = Database.from_shot(shot)
        LOGGER.debug('Database: %s', database.name)
        module = database['shot_task']
        id_list = module.filter(cgtwq.Filter('shot.shot', shot) &
                                cgtwq.Filter('pipeline', pipeline))
        if len(id_list) > 1:
            LOGGER.warning('Duplicated task: %s', shot)
            select = module.select(*id_list)
            current_account_id = cgtwq.util.current_account_id()
            data = select.get_fields('id', 'account_id')
            data = {i[0]: i[1] for i in data}

            def _by_artist(id_):
                task_account_id = data[id_]
                if not task_account_id:
                    return 2
                if current_account_id in task_account_id:
                    return 0
                return 1
            id_list = sorted(id_list, key=_by_artist)

        ret = cls(module, id_list[0])
        ret.shot = shot
        return ret


def dialog_login():
    """Login teamwork.  """
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
                traytip('CGTeamWork', '登录失败')
                continue
            traytip('CGTeamWork', '登录成功')
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


import callback


def setup():
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(cgtwq.update_setting)
