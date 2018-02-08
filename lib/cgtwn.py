# -*- coding=UTF-8 -*-
"""
cgteamwork integration with nuke.
"""

from __future__ import absolute_import, unicode_literals, print_function

import os
import logging
import webbrowser
from functools import wraps

import nuke

from wlf import cgtwq
from wlf.path import PurePath, get_unicode as u
from wlf.files import copy
from wlf.notify import CancelledError, Progress, traytip
import wlf.config

from edit import CurrentViewer
from node import Last
from nuketools import utf8, UTF8Object
from functools import wraps

LOGGER = logging.getLogger('com.wlf.cgtwn')


class Config(wlf.config.Config):
    """Comp config.  """
    default = {
        'csheet_database': 'proj_big',
        'csheet_prefix': 'SNJYW_EP14_',
        'csheet_outdir': 'E:/',
        'csheet_checked': False,
    }
    path = os.path.expanduser('~/.nuke/wlf.comp.json')


def abort_modified(func):
    """(Decorator)Abort function when project has been modified."""

    @wraps(func)
    def _func():
        if nuke.Root().modified():
            return False
        return func()
    return _func


def abort_when_module_not_enable(func):
    """(Decorator)Abort function if MODULE_ENABLE is not true."""

    @wraps(func)
    def _func():
        if not cgtwq.MODULE_ENABLE:
            return
        return func()
    return _func


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


class CurrentShot(cgtwq.Shot):
    """The shot of current script.  """

    def __init__(self):
        cgtwq.Shot.__init__(self, self.name)

    @classmethod
    def get_info(cls):
        """The project info.  """
        return cgtwq.proj_info(shot_name=cls.get_name())

    @classmethod
    def get_name(cls):
        """The current shot name.  """
        return PurePath(Last.name).shot

    @property
    def name(self):
        """The current shot name.  """
        return self.get_name()

    @property
    def workfile(self):
        """The path of current nk_file.  """
        return Last.name

    @property
    def image(self):
        """The rendered single image.  """
        return Last.jpg_path

    @property
    def video(self):
        """The rendered single image.  """
        return Last.mov_path

    def upload_image(self):
        """Upload imge to server and record it to cgtw database.  """

        LOGGER.debug('Uploading image to cgtw.')
        ret = copy(self.image, self.image_dest)
        if ret:
            self.shot_image = ret
        return ret

    def submit_image(self):
        """Upload .jpg to server then sumbit these files."""
        self.upload_image()
        self.submit([self.image_dest])

    def submit_video(self):
        """Upload .mov to server then sumbit these files."""

        copy(self.video, self.video_dest)
        self.submit([self.video_dest])

    @check_login(False)
    def ask_add_note(self):
        """Show a dialog for self.add_note function."""

        note = nuke.getInput(utf8('note内容'), utf8('来自nuke的note'))
        if note:
            self.add_note(note)


def check_with_upstream():
    """Check if script setting match upstream.  """

    nodes = {
        '动画视频': 'animation'
    }
    root = nuke.Root()
    msg = []
    first = root['first_frame'].value()
    last = root['last_frame'].value()
    current = {
        'frame_count': last - first + 1,
        'fps': root['fps'].value()
    }
    shot = CurrentShot()
    info = shot.get_info()
    default_fps = info.get('fps', 30)
    videos = shot.upstream_videos()
    row_format = '<tr><td>{0}</td><td>{1[frame_count]:.0f}帧</td><td>{1[fps]:.0f}fps</td></tr>'

    LOGGER.debug('Upstream videos: %s', videos)

    has_video_node = False
    input_num = 4
    for name, pipeline in nodes.items():
        n = nuke.toNode(utf8(name))
        if n is None:
            video = videos.get(pipeline)
            if video:
                n = nuke.nodes.Read(name=utf8(name))
                n[utf8('file')].fromUserText(video)
            else:
                LOGGER.debug('Can not get video: %s', pipeline)
                continue
        has_video_node = True
        n['frame_mode'].setValue('start_at')
        n['frame'].setValue(unicode(first))
        CurrentViewer().link(n.obj, input_num, replace=False)
        input_num += 1
        upstream = {
            'frame_count':  n['origlast'].value() - n['origfirst'].value() + 1,
            'fps': n.metadata('input/frame_rate') or default_fps
        }
        if upstream != current:
            msg.append(row_format.format(name, upstream))

    if msg:
        msg.insert(0, row_format.format('当前', current))
        style = '<style>td{padding:8px;}</style>'
        msg = '<font color="red">工程和上游不一致</font><br>'\
            '<table><th columnspan=3>{}<th>{}</table><hr>{}'.format(
                shot.name, ''.join(msg),
                '{} 默认fps:{}'.format(info.get('name'), default_fps))
        nuke.message(utf8(style + msg))
    elif not has_video_node:
        if current['fps'] != default_fps:
            confirm = nuke.ask(utf8(
                '当前fps: {}, 设为默认值: {} ?'.format(current['fps'], default_fps)))
            if confirm:
                nuke.knob('root.fps', utf8(default_fps))


def check_fx():
    """Check if has fx footage.  """

    info = CurrentShot().task_module.get_filebox_with_sign('fx')
    if info:
        dir_ = info['path']
        if os.listdir(dir_):
            nuke.message(utf8('此镜头有特效素材'))
            webbrowser.open(dir_)


@abort_when_module_not_enable
@check_login(False)
def on_load_callback():
    """Show cgtwn status"""

    try:
        check_with_upstream()
        check_fx()
        traytip('当前CGTeamWork项目', '{}:合成'.format(
            CurrentShot().info.get('name')))

    except cgtwq.LoginError:
        traytip('Nuke无法访问数据库', '请登录CGTeamWork')
    except cgtwq.IDError as ex:
        traytip('CGteamwork找不到对应条目', u(ex))


@abort_when_module_not_enable
@check_login(True)
def on_save_callback():
    """Try upload nk file to server."""

    if nuke.GUI:
        try:
            check_with_upstream()
            shot = CurrentShot()
            shot.check_account()
            dst = copy(shot.workfile, shot.workfile_dest)
            if dst:
                traytip('更新文件', dst)
        except cgtwq.LoginError:
            traytip('需要登录', '请尝试从Nuke的CGTeamWork菜单登录帐号或者重启电脑')
        except cgtwq.IDError:
            traytip('更新文件', 'CGTW上未找到对应镜头')
        except cgtwq.AccountError as ex:
            traytip('未更新文件',
                    '当前镜头已被分配给:\t{}\n当前用户:\t\t{}'.format(ex.owner or '<未分配>', ex.current))


@abort_when_module_not_enable
@abort_modified
@check_login(False)
def on_close_callback():
    """Try upload image to server."""

    on_save_callback()
    try:
        nuke.scriptName()
    except RuntimeError:
        LOGGER.warning('尝试在未保存时上传单帧')
        return
    try:
        shot = CurrentShot()
        shot.check_account()
        if not shot.image:
            traytip('未更新单帧', '找不到单帧路径')
            return

        dst = shot.upload_image()
        if dst:
            traytip('更新单帧', dst)
    except OSError:
        traytip('未更新单帧', '找不到文件 {}'.format(shot.image))
    except cgtwq.LoginError:
        traytip('需要登录', '请尝试从Nuke的CGTeamWork菜单登录帐号或者重启电脑')
    except cgtwq.IDError as ex:
        traytip('未更新单帧', 'CGTW上未找到对应镜头\n {}'.format(ex))
    except cgtwq.AccountError as ex:
        traytip('未更新单帧',
                '当前镜头已被分配给:\t{}\n当前用户:\t\t{}'.format(ex.owner or '<未分配>', ex.current))
    except Exception as ex:
        LOGGER.error('Unexpected exception', exc_info=True)
        raise


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

    folder_input_name = '输出文件夹'
    database_input_name = '数据库'
    prefix_input_name = '镜头名前缀限制'
    panel = nuke.Panel(utf8('为项目创建文件夹'))
    panel.addSingleLineInput(database_input_name, 'proj_qqfc_2017')
    panel.addSingleLineInput(prefix_input_name, '')
    panel.addFilenameSearch(folder_input_name, 'E:/temp')
    confirm = panel.show()
    if not confirm:
        return

    try:
        task = Progress('创建文件夹')
        database = panel.value(database_input_name)
        save_path = panel.value(folder_input_name)
        prefix = panel.value(prefix_input_name)

        task.set(10)
        try:
            names = cgtwq.Shots(database, prefix=prefix).shots
        except cgtwq.IDError as ex:
            nuke.message(utf8('找不到对应条目\n{}'.format(ex)))
            return
        task.set(20)

        for name in names:
            _path = os.path.join(save_path, name)
            if not os.path.exists(_path):
                os.makedirs(_path)
        webbrowser.open(save_path)
    except CancelledError:
        LOGGER.debug('用户取消创建文件夹')
