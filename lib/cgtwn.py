# -*- coding=UTF-8 -*-
"""
cgteamwork integration with nuke.
"""
import os
import logging
import threading
import time
import webbrowser

import nuke

from wlf import cgtwq, csheet, files
from wlf.path import remove_version
from wlf.notify import CancelledError, Progress, traytip
import wlf.config

from asset import copy
from node import Last

__version__ = '0.9.16'

LOGGER = logging.getLogger('com.wlf.cgtwn')


class Config(wlf.config.Config):
    """Comp config.  """
    default = {
        'csheet_database': 'proj_big',
        'csheet_prefix': 'SNJYW_EP14_',
        'csheet_outdir': 'E:/',
        'csheet_checked': False,
    }
    path = os.path.expanduser(u'~/.nuke/wlf.comp.json')


def abort_modified(func):
    """(Decorator)Abort function when project has been modified."""

    def _func():
        if nuke.Root().modified():
            return False
        func()
    return _func


def abort_when_module_not_enable(func):
    """(Decorator)Abort function if MODULE_ENABLE is not true."""

    def _func():
        if not cgtwq.MODULE_ENABLE:
            return
        func()
    return _func


def check_login(update=False):
    """(Decorator)Abort funciton if not logged in."""
    def _deco(func):
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
        return remove_version(os.path.splitext(os.path.basename(Last.name))[0])

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

        note = nuke.getInput(
            u'note内容'.encode('UTF-8'),
            u'来自nuke的note'.encode('UTF-8')
        )
        if note:
            self.add_note(note)


@abort_when_module_not_enable
@check_login(False)
def on_load_callback():
    """Show cgtwn status"""

    def _run():
        try:
            traytip('当前CGTeamWork项目', '{}:合成'.format(
                CurrentShot().info.get('name')))
        except cgtwq.LoginError:
            traytip('Nuke无法访问数据库', '请登录CGTeamWork')
        except cgtwq.IDError as ex:
            traytip('CGteamwork找不到对应条目', str(ex))

    threading.Thread(target=_run).start()


@abort_when_module_not_enable
@check_login(True)
def on_save_callback():
    """Try upload nk file to server."""

    def _run():
        try:
            shot = CurrentShot()
            shot.check_account()
            dst = copy(shot.workfile, shot.workfile_dest)
            if dst:
                traytip('更新文件', dst)
        except cgtwq.LoginError:
            traytip('需要登录', u'请尝试从Nuke的CGTeamWork菜单登录帐号或者重启电脑')
        except cgtwq.IDError:
            traytip('更新文件', u'CGTW上未找到对应镜头')
        except cgtwq.AccountError as ex:
            traytip('未更新文件',
                    '当前镜头已被分配给:\t{}\n当前用户:\t\t{}'.format(ex.owner or '<未分配>', ex.current))

    threading.Thread(target=_run).start()


@abort_when_module_not_enable
@abort_modified
@check_login(False)
def on_close_callback():
    """Try upload image to server."""

    try:
        nuke.scriptName()
    except RuntimeError:
        LOGGER.warning('尝试在未保存时上传单帧')
        return
    try:
        shot = CurrentShot()
        shot.check_account()
        start_time = time.time()
        # Wait on close jpg rendering.
        while True:
            mtime = os.path.getmtime(shot.image)
            if mtime - start_time > -10:
                break
            elif time.time() - start_time > 10:
                LOGGER.warning('单帧等待时间超时: %s', shot.image)
                break
            time.sleep(1)
        dst = shot.upload_image()
        if dst:
            traytip('更新单帧', dst)
    except cgtwq.LoginError:
        traytip('需要登录', u'请尝试从Nuke的CGTeamWork菜单登录帐号或者重启电脑')
    except cgtwq.IDError:
        traytip('更新单帧', u'CGTW上未找到对应镜头')
    except cgtwq.AccountError as ex:
        traytip('未更新单帧',
                '当前镜头已被分配给:\t{}\n当前用户:\t\t{}'.format(ex.owner or '<未分配>', ex.current))


class ContactSheetPanel(object):
    """Panel for html contactsheet creation.  """
    edits = [
        ('SingleLineInput', 'csheet_database', '数据库'),
        ('SingleLineInput', 'csheet_prefix', '镜头名前缀限制'),
        ('FilenameSearch', 'csheet_outdir', '输出文件夹'),
        ('BooleanCheckBox', 'csheet_checked', '忽略不存在的图像'),
        ('BooleanCheckBox', 'csheet_save_images', '打包到本地'),
    ]
    default = {
        'csheet_save_images': False
    }

    def __init__(self):
        self._config = Config()
        self._panel = nuke.Panel('为项目创建HTML色板')
        for i in self.edits:
            default = self.default.get(i[1]) or self._config.get(i[1])
            getattr(self._panel, 'add{}'.format(i[0]))(i[2], default)

    @check_login(True)
    def show(self):
        """Show the panel.  """
        confirm = self._panel.show()
        if not confirm:
            return

        try:
            task = Progress('创建色板')
            database = self.get('csheet_database')
            prefix = self.get('csheet_prefix')
            outdir = self.get('csheet_outdir')
            save_path = os.path.join(outdir,
                                     u'{}_{}_色板.html'.format(database, prefix.strip('_')))

            task.set(message='访问数据库文件')
            try:
                images = cgtwq.Shots(database, prefix=prefix).get_all_image()
            except cgtwq.IDError as ex:
                nuke.message('找不到对应条目\n{}'.format(ex))
                return
            except RuntimeError:
                return

            if self.get('csheet_checked'):
                images = files.checked_exists(images)

            task.set(50, '生成文件')
            if self.get('csheet_save_images'):
                task = Progress('下载图像到本地', total=len(images))
                for f in images:
                    task.step(f)
                    image_dir = os.path.join(
                        outdir, '{}_images/'.format(database))
                    copy(f, image_dir)
                created_file = csheet.create_html_from_dir(image_dir)
            else:
                created_file = csheet.create_html(images, save_path,
                                                  title=u'色板 {}@{}'.format(prefix, database))
            if created_file:
                webbrowser.open(created_file)
        except CancelledError:
            LOGGER.debug(u'用户取消创建色板')

    def get(self, key, default=None):
        """Get value from panel.  """
        try:
            name = [i for i in self.edits if i[1] == key][0][2]
            ret = self._panel.value(name)
            self._config[key] = ret
            return ret
        except IndexError:
            return default


def dialog_login():
    """Login teamwork.  """
    account = '帐号'
    password = '密码'
    panel = nuke.Panel('登录CGTeamWork')
    panel.addSingleLineInput('帐号', '')
    panel.addPasswordInput('密码', '')

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
    panel = nuke.Panel('为项目创建文件夹')
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
            nuke.message('找不到对应条目\n{}'.format(ex))
            return
        task.set(20)

        for name in names:
            _path = os.path.join(save_path, name)
            if not os.path.exists(_path):
                os.makedirs(_path)
        webbrowser.open(save_path)
    except CancelledError:
        LOGGER.debug(u'用户取消创建文件夹')
