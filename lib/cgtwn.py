# -*- coding=UTF-8 -*-
"""
cgteamwork integration with nuke.
"""
import os

import nuke

from wlf import cgtwq, csheet, files
from wlf.files import remove_version, traytip, url_open
from wlf.progress import CancelledError, Progress

from asset import copy
from config import Config
from node import wlf_write_node

__version__ = '0.9.7'


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


def proj_info():
    """Return current project info by script name.  """

    qqfc2017 = {'database': u'proj_qqfc_2017',
                'shot_task_folder': u'shot_work'}
    snjyw = {'database': u'proj_big',
             'shot_task_folder': u'shot_work'}

    ret = qqfc2017
    name = os.path.basename(nuke.value('root.name'))
    if name.startswith('SNJYW'):
        ret = snjyw
    return ret


class CurrentShot(cgtwq.Shot):
    """The shot of current script.  """

    def __init__(self):
        cgtwq.Shot.__init__(self, self.name)

    @property
    def name(self):
        """The current shot name.  """
        return remove_version(os.path.splitext(os.path.basename(nuke.scriptName()))[0])

    @property
    def workfile(self):
        """The path of current nk_file.  """
        return nuke.scriptName()

    @property
    def image(self):
        """The rendered single image.  """
        return os.path.join(nuke.value(
            'root.project_directory', ''), nuke.filename(wlf_write_node().node('Write_JPG_1')))

    @property
    def video(self):
        """The rendered single image.  """
        return os.path.join(nuke.value(
            'root.project_directory', ''), nuke.filename(wlf_write_node().node('Write_MOV_1')))

    def upload_image(self):
        """Upload imge to server and record it to cgtw database.  """
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
    try:
        traytip('当前CGTeamWork项目', '{}:合成'.format(
            CurrentShot().info.get('name')))
    except cgtwq.LoginError:
        traytip('Nuke无法访问数据库', '请登录CGTeamWork')
    except cgtwq.IDError as ex:
        traytip('CGteamwork找不到对应条目', str(ex))


@abort_when_module_not_enable
@check_login(True)
def on_save_callback():
    """Try upload nk file to server."""
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


@abort_when_module_not_enable
@abort_modified
@check_login(False)
def on_close_callback():
    """Try upload image to server."""
    try:
        nuke.scriptName()
    except RuntimeError:
        return
    try:
        shot = CurrentShot()
        shot.check_account()
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


@check_login(True)
def dialog_create_csheet():
    """A dialog for create html from cgtwq.  """
    config = Config()

    folder_input_name = '输出文件夹'
    database_input_name = '数据库'
    prefix_input_name = '镜头名前缀限制'
    check_input_name = '忽略不存在的图像'
    save_images_name = '打包到本地'
    panel = nuke.Panel('为项目创建HTML色板')
    panel.addSingleLineInput(
        database_input_name, config.get('csheet_database'))
    panel.addSingleLineInput(prefix_input_name, config.get('csheet_prefix'))
    panel.addFilenameSearch(folder_input_name, config.get('csheet_outdir'))
    panel.addBooleanCheckBox(check_input_name, False)
    panel.addBooleanCheckBox(
        save_images_name, config.get('csheet_save_images'))
    confirm = panel.show()
    if not confirm:
        return

    try:
        task = Progress('创建色板')
        config['csheet_database'] = panel.value(database_input_name)
        config['csheet_outdir'] = panel.value(folder_input_name)
        config['csheet_prefix'] = panel.value(prefix_input_name)
        config['csheet_checked'] = panel.value(check_input_name)
        config['csheet_save_images'] = panel.value(save_images_name)

        save_path = os.path.join(config['csheet_outdir'],
                                 u'{}色板.html'.format(config['csheet_database']))

        task.set(message='访问数据库文件')
        try:
            images = cgtwq.Shots(
                config['csheet_database'], prefix=config['csheet_prefix']).get_all_image()
        except cgtwq.IDError as ex:
            nuke.message('找不到对应条目\n{}'.format(ex))
            return
        except RuntimeError:
            return

        if config['csheet_checked']:
            images = files.checked_exists(images)

        task.set(50, '生成文件')
        if config['csheet_save_images']:
            task = Progress('下载图像到本地')
            all_num = len(images)
            for index, f in enumerate(images):
                task.set(index * 100 // all_num, f)
                image_dir = os.path.join(config['csheet_outdir'],
                                         '{}_images/'.format(config['csheet_database']))
                copy(f, image_dir)
            created_file = csheet.create_html_from_dir(image_dir)
        else:
            created_file = csheet.create_html(images, save_path,
                                              title=u'色板 {}'.format(config['csheet_database']))
        if created_file:
            url_open(created_file, isfile=True)
    except CancelledError:
        print('用户取消创建色板')


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
        url_open(save_path, isfile=True)
    except CancelledError:
        print('用户取消创建文件夹')
