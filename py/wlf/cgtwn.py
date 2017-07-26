# -*- coding=UTF-8 -*-
"""
cgteamwork integration with nuke.
"""
import locale
import os
import re
import sys
from subprocess import Popen, PIPE

import nuke

from .asset import copy


CGTW_PATH = r"C:\cgteamwork\bin\base"
MODULE_ENABLE = True
try:
    sys.path.append(CGTW_PATH)
    import cgtw
except ImportError:
    if not os.path.isdir(CGTW_PATH):
        raise ImportError('not a dir: {}'.format(CGTW_PATH))
    else:
        MODULE_ENABLE = False


__version__ = '0.4.5'
SYS_CODEC = locale.getdefaultlocale()[1]
reload(sys)
sys.setdefaultencoding('UTF-8')


def abort_modified(func):
    """(Decorator)Abort function when project has been modified."""

    def _func():
        if nuke.modified():
            return False
        func()
    return _func


def abort_when_module_not_enable(func):
    """(Decorator)Abort function if MODULE_ENABLE is not true."""

    def _func():
        if not MODULE_ENABLE:
            return
        func()
    return _func


def check_login(func):
    """(Decorator)Abort funciton if not logged in."""

    def _func(*args, **kwargs):
        if CGTeamWork.is_logged_in:
            func(*args, **kwargs)
        else:
            print(func.__name__, 'not login, abort.')

    return _func


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


class CGTeamWork(object):
    """Base class for cgtw action."""

    is_logged_in = False

    def __init__(self):
        self._tw = cgtw.tw()

    @property
    def database(self):
        """database on cgtw.  """
        return proj_info()['database']

    @staticmethod
    def update_status():
        """Return and set if cls.is_logged_in."""

        task = nuke.ProgressTask('尝试连接CGTeamWork')
        task.setProgress(50)
        if not CGTeamWork.is_running():
            ret = False
        else:
            ret = cgtw.tw().sys().get_socket_status()
            print(u'CGTeamWork连接正常' if ret else u'CGTeamWork未连接')
        CGTeamWork.is_logged_in = ret
        return ret

    @classmethod
    def set_database(cls, database):
        """Set class.database attribute."""

        cls.database = database

    @classmethod
    def ask_database(cls):
        """Show a dialog ask user database then set."""

        database = nuke.getInput(u'工程英文名称'.encode('UTF-8'), cls.database)
        if database:
            cls.set_database(database)

    @staticmethod
    def is_running():
        """Return is CgTeamWork.exe is running.  """

        ret = True
        if sys.platform == 'win32':
            tasklist = Popen('TASKLIST', stdout=PIPE).communicate()[0]
            if '\nCGTeamWork.exe ' in tasklist:
                ret = False
                nuke.warning(u'未运行 CGTeamWork.exe 。')
        return ret


class Shot(CGTeamWork):
    """Methods for shot action."""

    pipeline = u'合成'
    pipeline_name = u'comp'
    module = u'shot_task'
    work_folder = u'work'

    image_folder = u'Image'
    server = u'Z:\\CGteamwork_Test'

    def __init__(self):
        super(Shot, self).__init__()
        self._task_module = self._tw.task_module(
            self.database, self.module)

        self._task_module.init_with_id(self.shot_id)

    @property
    def shot_task_folder(self):
        """shot_task_folder on server.  """
        return proj_info()['shot_task_folder']

    @property
    def name(self):
        """The shot.shot name for cgtw."""

        ret = nuke.value('root.name', '')
        ret = os.path.basename(ret)
        ret = os.path.splitext(ret)[0]
        ret = re.sub(r'_v\d+$', '', ret)
        return ret

    @property
    def shot_id(self):
        """The id attribute of shot on cgtw."""

        id_list = self._task_module.get_with_filter(
            [], [['shot.shot', '=', self.name], ['shot_task.pipeline', '=', self.pipeline]])
        if not id_list:
            raise IDError(self.database, self.module,
                          self.pipeline, self.name)
        elif len(id_list) is not 1:
            raise IDError(u'多个符合的条目'.encode('UTF-8'), id_list)
        ret = id_list[0]['id']
        return ret

    def get_property(self, property_name):
        """Return property value from cgtw."""

        info = self._task_module.get([property_name])[0]
        return info[property_name]

    @property
    def workfile_dest(self):
        """The .nk file upload destination."""

        infos = self._task_module.get(
            ['shot.shot', 'eps.project_code', 'eps.eps_name'])[0]
        ret = os.path.join(
            self.server,
            infos['eps.project_code'],
            self.shot_task_folder,
            self.pipeline_name,
            infos['eps.eps_name'],
            infos['shot.shot'],
            self.work_folder
        ) + '\\'
        if not os.path.isdir(os.path.dirname(ret)):
            raise FolderError(ret)
        return ret

    @property
    def image_dest(self):
        """The .jpg file upload destination."""

        infos = self._task_module.get(
            ['shot.shot', 'eps.project_code', 'eps.eps_name'])[0]
        ret = os.path.join(
            self.server,
            infos['eps.project_code'],
            self.shot_task_folder,
            self.pipeline_name,
            infos['eps.eps_name'],
            infos['shot.shot'],
            self.image_folder,
            infos['shot.shot'] + '.jpg'
        )
        if not os.path.isdir(os.path.dirname(ret)):
            raise FolderError(ret)
        return ret

    @property
    def video_dest(self):
        """The .mov file upload destination."""

        infos = self._task_module.get(
            ['shot.shot', 'eps.project_code', 'eps.eps_name'])[0]
        ret = os.path.join(
            self.server,
            infos['eps.project_code'],
            'shot/avi',
            self.pipeline_name,
            infos['eps.eps_name'],
            'check',
            infos['shot.shot'] + '.mov'
        )
        if not os.path.isdir(os.path.dirname(ret)):
            raise FolderError(ret)
        return ret

    @check_login
    def submit(self, files, folders=None, note=u'自nuke提交'):
        """Submit this shot to cgtw."""
        if not folders:
            folders = []
        print(u'提交: {}'.format(files + folders))
        ret = self._task_module.submit(files, note, folders)
        if not ret:
            print('提交失败')
        return ret

    @check_login
    def upload_nk_file(self):
        """Upload .nk file to server."""

        src = nuke.scriptName()
        dst = self.workfile_dest
        copy(src, dst)

    @check_login
    def upload_image(self):
        """Uploade .jpg file to server."""

        n = nuke.toNode('_Write') or nuke.toNode(
            'wlf_Write1') or nuke.allNodes('wlf_Write')
        if isinstance(n, list):
            n = n[0]
        if n:
            src = os.path.join(nuke.value(
                'root.project_directory', ''), nuke.filename(n.node('Write_JPG_1')))
            if not os.path.exists(src):
                return
            dst = self.image_dest
            if not (os.path.exists(dst) and (
                    os.path.getmtime(src) - os.path.getmtime(dst) < 1e-06)):
                copy(src, dst)
            return dst

    @check_login
    def upload_video(self):
        """Uploade .mov file to server."""

        n = nuke.toNode('_Write') or nuke.toNode(
            'wlf_Write1') or nuke.allNodes('wlf_Write')
        if isinstance(n, list):
            n = n[0]
        if n:
            src = os.path.join(nuke.value(
                'root.project_directory', ''), nuke.filename(n.node('Write_MOV_1')))
            dst = self.video_dest
            if not (os.path.exists(dst) and (
                    os.path.getmtime(src) - os.path.getmtime(dst) < 1e-06)):
                copy(src, dst)
            return dst

    def submit_image(self):
        """Upload .jpg to server then sumbit these files."""
        self.upload_image()
        self.submit([self.image_dest])

    def submit_video(self):
        """Upload .mov to server then sumbit these files."""

        self.upload_video()
        self.submit([self.video_dest])

    def add_note(self, note):
        """Add note for this shot on cgtw."""

        self._task_module.create_note(note)

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
@abort_modified
def on_save_callback():
    """Try upload nk file to server."""

    try:
        CGTeamWork.update_status()
        Shot().upload_nk_file()
    except IDError:
        print(u'CGTW上未找到对应镜头')


@abort_when_module_not_enable
@abort_modified
def on_close_callback():
    """Try upload image to server."""
    try:
        Shot().upload_image()
    except IDError:
        print(u'CGTW上未找到对应镜头')


class IDError(Exception):
    """Indicate can't specify shot id on cgtw."""

    def __init__(self, *args):
        Exception.__init__(self)
        self.message = args

    def __str__(self):
        return '找不到对应条目:{}'.format(self.message)


class FolderError(Exception):
    """Indicate can't found destination folder."""

    def __init__(self, *args):
        Exception.__init__(self)
        self.message = args

    def __str__(self):
        return '服务器上无对应文件夹:{}'.format(self.message)


class LoginError(Exception):
    """Indicate haven't been login to cgtw."""

    def __str__(self):
        return 'CGTeamWork服务器未连接'
