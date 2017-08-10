# -*- coding=UTF-8 -*-
"""
cgteamwork integration with nuke.
"""
# TODO: check account
import os

import nuke

from . import cgtwq, csheet, files
from .asset import copy
from .files import url_open, traytip, remove_version
from .node import wlf_write_node


__version__ = '0.7.3'


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
                    nuke.message('未登录CGTeamWork')
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

    def submit_image(self):
        """Upload .jpg to server then sumbit these files."""
        copy(self.image, self.image_dest)
        self.submit([self.image_dest])

    def submit_video(self):
        """Upload .mov to server then sumbit these files."""

        copy(self.video, self.video_dest)
        self.submit([self.video_dest])

    @check_login
    def ask_add_note(self):
        """Show a dialog for self.add_note function."""

        note = nuke.getInput(
            u'note内容'.encode('UTF-8'),
            u'来自nuke的note'.encode('UTF-8')
        )
        if note:
            self.add_note(note)


@abort_when_module_not_enable
def on_load_callback():
    """Show cgtwn status"""
    traytip('当前CGTeamWork项目', '{}:合成'.format(CurrentShot().info.get('name')))


@abort_when_module_not_enable
@abort_modified
def on_save_callback():
    """Try upload nk file to server."""

    try:
        shot = CurrentShot()
    except cgtwq.IDError:
        traytip('更新文件', u'CGTW上未找到对应镜头')
    dst = copy(shot.workfile, shot.workfile_dest)
    if dst:
        traytip('更新文件', dst)


@abort_when_module_not_enable
@abort_modified
def on_close_callback():
    """Try upload image to server."""
    try:
        shot = CurrentShot()
    except cgtwq.IDError:
        traytip('更新单帧', u'CGTW上未找到对应镜头')

    dst = copy(shot.image, shot.image_dest)
    if dst:
        traytip('更新单帧', dst)


@check_login(True)
def dialog_create_csheet():
    """A dialog for create html from cgtwq.  """

    folder_input_name = '输出文件夹'
    database_input_name = '数据库'
    prefix_input_name = '镜头名前缀限制'
    check_input_name = '忽略不存在的图像'
    panel = nuke.Panel('为项目创建HTML色板')
    panel.addSingleLineInput(database_input_name, 'proj_qqfc_2017')
    panel.addSingleLineInput(prefix_input_name, '')
    panel.addFilenameSearch(folder_input_name, 'E:/')
    panel.addBooleanCheckBox(check_input_name, True)
    confirm = panel.show()
    if not confirm:
        return

    task = nuke.ProgressTask('创建色板')
    database = panel.value(database_input_name)
    save_path = os.path.join(panel.value(
        folder_input_name), u'{}色板.html'.format(database))
    prefix = panel.value(prefix_input_name)
    checked = panel.value(check_input_name)

    task.setProgress(10)
    try:
        images = cgtwq.Shots(database).get_all_image(prefix)
    except cgtwq.IDError as ex:
        nuke.message('找不到对应条目\n{}'.format(ex))
        return
    task.setProgress(20)
    if checked:
        images = files.checked_exists(images)
    created_file = csheet.create_html(images, save_path,
                                      title=u'色板 {}'.format(database))
    if created_file:
        url_open(created_file, isfile=True)


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
                nuke.message('登录失败')
            else:
                nuke.message('登录成功')
