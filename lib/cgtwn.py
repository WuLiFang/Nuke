# -*- coding=UTF-8 -*-
"""
cgteamwork integration with nuke.
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import webbrowser
from functools import wraps

import nuke

from edit import CurrentViewer
from nuketools import utf8
from wlf import cgtwq
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


def check_login(update=False):
    """(Decorator)Abort funciton if not logged in."""

    def _deco(func):

        @wraps(func)
        def _func(*args, **kwargs):
            if update:
                cgtwq.CGTeamWork.update_status()
            if cgtwq.CGTeamWork.is_logged_in:
                return func(*args, **kwargs)
            else:
                if nuke.GUI:
                    traytip('警告', 'CGTeamWork未登录', options=2)
        return _func
    return _deco


class Task(cgtwq.database.Selection):
    """Selection for single shot.  """

    def __init__(self, shot, pipeline='合成'):
        self.shot = shot
        database = Database.from_shot(shot)
        LOGGER.debug('Database: %s', database.name)
        module = database['shot_task']
        id_list = module.filter(cgtwq.Filter('shot.shot', shot) &
                                cgtwq.Filter('pipeline', pipeline))
        if len(id_list) > 1:
            LOGGER.warning('Duplicated task: %s', shot)
            select = cgtwq.database.Selection(id_list, module)
            current_account_id = cgtwq.server.account_id()
            data = select.get_fields('id', 'account_id')
            data = {i[0]: i[1] for i in data}

            def _by_artist(id_):
                task_account_id = data[id_]
                if not task_account_id:
                    return 2
                if current_account_id in task_account_id:
                    return 0
                return 1
            id_list = [sorted(id_list, key=_by_artist)[0]]

        super(Task, self).__init__(id_list, module)

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
                n = nuke.nodes.Read(name=utf8(node_name),
                                    file=utf8(video.as_posix()))
                break
        n['frame_mode'].setValue(b'start_at')
        n['frame'].setValue(b'{:.0f}'.format(
            nuke.numvalue('root.first_frame')))
        CurrentViewer().link(n, 4, replace=False)
        return n

    def __getitem__(self, name):
        ret = super(Task, self).__getitem__(name)
        if isinstance(name, int):
            return ret
        assert len(self) == 1
        return ret[0]


def dialog_login():
    """Login teamwork.  """
    account = '帐号'
    password = '密码'
    panel = nuke.Panel(utf8('登录CGTeamWork'))
    panel.addSingleLineInput(utf8('帐号'), '')
    panel.addPasswordInput(utf8('密码'), '')

    success = False
    while not success:
        confirm = panel.show()
        if confirm:
            success = cgtwq.CGTeamWork().login(panel.value(account), panel.value(password))
            if not success:
                traytip('CGTeamWork', '登录失败')
            else:
                traytip('CGTeamWork', '登录成功')
        else:
            break


@check_login(True)
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
                names = cgtwq.Shots(database, prefix=prefix).shots
            except cgtwq.IDError as ex:
                nuke.message(utf8('找不到对应条目\n{}'.format(ex)))
                return

        for name in progress(names, '创建文件夹'):
            _path = os.path.join(save_path, name)
            if not os.path.exists(_path):
                os.makedirs(_path)
        webbrowser.open(save_path)
    except CancelledError:
        LOGGER.debug('用户取消创建文件夹')
