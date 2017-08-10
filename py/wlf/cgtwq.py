# -*- coding=UTF-8 -*-
"""Query info from cgteamwork.

should compatible by any cgteamwork bounded python executable.
"""

import os
import sys

from subprocess import Popen, PIPE


try:
    import nuke
    HAS_NUKE = True
except ImportError:
    HAS_NUKE = False

__version__ = '0.2.4'

CGTW_PATH = r"C:\cgteamwork\bin\base"
CGTW_EXECUTABLE = r"C:\cgteamwork\bin\cgtw\CgTeamWork.exe"
MODULE_ENABLE = True
try:
    if os.path.isdir(CGTW_PATH):
        sys.path.append(CGTW_PATH)
        import cgtw
    else:
        raise ImportError(u'not a dir: {}'.format(CGTW_PATH))
except ImportError:
    print(u'**错误**导入cgtw模块失败, CGTeamWork相关功能失效。')
    MODULE_ENABLE = False

SERVER_PATH = u'Z:\\CGteamwork_Test'


def proj_info(shot_name=None, database=None):
    """Return current project info by @shot_name or by @database.  """

    default = {'database': u'proj_qqfc_2017',
               'name': u'QQ飞车2017(默认)',
               'module': u'shot_task',
               'pipeline': u'合成',
               'pipeline_name': u'comp',
               'shot_task_folder_name': u'shot_work',
               'image_folder_name': u'Image',
               'work_folder': u'work',
               'image_dest_pat': '\\'.join([
                   SERVER_PATH,
                   '{0[eps.project_code]}',
                   '{0[shot_task_folder_name]}',
                   '{0[pipeline_name]}',
                   '{0[eps.eps_name]}',
                   '{0[shot.shot]}',
                   '{0[image_folder_name]}',
                   '{0[shot.shot]}.jpg'
               ]),
               'video_dest_pat': '\\'.join([
                   SERVER_PATH,
                   '{0[eps.project_code]}',
                   'shot/avi',
                   '{0[pipeline_name]}',
                   '{0[eps.eps_name]}',
                   'check',
                   '{0[shot.shot]}.mov'
               ]),
               'workfile_dest_pat':   '\\'.join([
                   SERVER_PATH,
                   '{0[eps.project_code]}',
                   '{0[shot_task_folder_name]}',
                   '{0[pipeline_name]}',
                   '{0[eps.eps_name]}',
                   '{0[shot.shot]}',
                   '{0[work_folder]}\\'
               ])}
    snjyw = {'database': u'proj_big',
             'name': u'少年锦衣卫'}
    mt = {'database': u'proj_mt',
          'name': u'梦塔'}
    prefixs = {'SNJYW': snjyw, 'MT': mt}
    all_info = (default, snjyw, mt)

    ret = dict(default)
    if database:
        for info in all_info:
            if info.get('database') == database:
                ret.update(info)
                break
    if shot_name:
        for prefix, info in prefixs.items():
            if shot_name.upper().startswith(prefix):
                ret.update(info)
                break
    return ret


class CGTeamWork(object):
    """Base class for cgtw action."""

    initiated_class = None
    is_logged_in = False
    _tw = None
    _task_module = None

    def __init__(self):
        super(CGTeamWork, self).__init__()
        if not CGTeamWork._tw:
            CGTeamWork._tw = cgtw.tw()

    @staticmethod
    def is_running():
        """Return is CgTeamWork.exe is running.  """

        ret = True
        if sys.platform == 'win32':
            tasklist = Popen('TASKLIST', stdout=PIPE).communicate()[0]
            if '\nCgTeamWork.exe ' not in tasklist:
                ret = False
                print(u'未运行 CGTeamWork.exe 。')
        return ret

    @staticmethod
    def update_status():
        """Return and set if cls.is_logged_in."""

        task = nuke.ProgressTask('尝试连接CGTeamWork')
        task.setProgress(50)
        if not CGTeamWork.is_running() and os.path.exists(CGTW_EXECUTABLE):
            ret = False
            Popen(CGTW_EXECUTABLE, cwd=os.path.dirname(CGTW_EXECUTABLE))
        else:
            ret = cgtw.tw().sys().get_socket_status()
        CGTeamWork.is_logged_in = ret
        print(u'CGTeamWork连接正常' if ret else u'CGTeamWork未连接')
        return ret

    def current_account(self):
        """Return current account.  """
        return self._tw.sys().get_account()

    def current_account_id(self):
        """Return current account id.  """
        return self._tw.sys().get_account_id()

    def submit(self, file_list, folders=None, note=u'自nuke提交'):
        """Submit current initiated item to cgtw."""
        if not folders:
            folders = []
        print(u'提交: {}'.format(file_list + folders))
        ret = self._task_module.submit(file_list, note, folders)
        if not ret:
            print('提交失败')
        return ret

    def add_note(self, note):
        """Add note for current initiated item on cgtw."""

        self._task_module.create_note(note)

    def login(self, account, password):
        ret = self._tw.sys().login(account, password)
        print ret
        return ret


class Shots(CGTeamWork):
    """Deal multple shot at once.  """

    def __init__(self, database, module=None, pipeline=None):
        super(Shots, self).__init__()
        self.database = database
        self._info = proj_info(database=database)
        self.module = module or self._info.get('module')
        self.pipeline = pipeline or self._info.get('pipeline')
        self._task_module = self._tw.task_module(self.database, self.module)

    def get_all_image(self, prefix=None):
        """Get all image dest for shots, can match shot with @prefix.  """

        filters = []
        if self.pipeline:
            filters.append(['shot_task.pipeline', '=', self.pipeline])
        initiated = self._task_module.init_with_filter(filters)
        if not initiated:
            raise IDError(self.database, filters)

        shots_info = self._task_module.get(['shot.shot'])
        shots = sorted(set(i['shot.shot']
                           for i in shots_info
                           if i['shot.shot'] and (not prefix or i['shot.shot'].startswith(prefix))))

        all_num = len(shots)
        images = []
        if HAS_NUKE:
            task = nuke.ProgressTask('查询数据库')

        def _progress(num, msg):
            if HAS_NUKE:
                task.setProgress(num)
                task.setMessage(msg)
        for index, shot in enumerate(shots):
            _progress(index * 100 // all_num, shot)
            try:
                image = Shot(shot, database=self.database).image_dest
            except IDError:
                continue

            images.append(image)

        return images


class Shot(CGTeamWork):
    """Methods for shot action."""

    def __init__(self, name, database=None):
        super(Shot, self).__init__()

        self._name = name
        if database:
            self._info = proj_info(database=database)
        else:
            self._info = proj_info(name)

        self._task_module = self._tw.task_module(self.database, self.module)

        id_list = self._task_module.get_with_filter(
            [], [['shot.shot', '=', self.name], ['shot_task.pipeline', '=', self.pipeline]])
        if not id_list:
            raise IDError(self.database, self.module,
                          self.pipeline, self.name)
        elif len(id_list) != 1:
            if ''.join(i['id'] for i in id_list) == u'please login!!!':
                raise LoginError
            raise IDError(u'Multiple match', id_list)
        self._id = id_list[0]['id']

        self._task_module.init_with_id(self.shot_id)

        self.update_info()

    def update_info(self):
        """Update info from database"""

        infos = self._task_module.get(
            ['shot.shot', 'eps.project_code',
             'eps.eps_name', 'shot_task.artist', 'shot_task.account_id'])[0]
        self._info.update(infos)

    @property
    def info(self):
        """The Shot info as a dictionary.  """
        return self._info

    @property
    def database(self):
        """The database current using.  """
        return self._info.get('database')

    @property
    def module(self):
        """The module current using(e.g. 'shot_task').  """
        return self._info.get('module')

    @property
    def pipeline(self):
        """The module current using(e.g. 'comp').  """
        return self._info.get('pipeline')

    @property
    def name(self):
        """The name of current shot(e.g. 'ep01_sc001').  """
        return self._name

    @property
    def shot_task_folder(self):
        """shot_task_folder on server.  """
        return self._info.get('shot_task_folder')

    @property
    def shot_id(self):
        """The id attribute of shot.  """
        return self._id

    @property
    def artist(self):
        """The aritist field on cgtw.  """
        return self._info.get('shot_task.artist')

    @property
    def artist_id(self):
        """The aritist_id field on cgtw.  """
        return self._info.get('shot_task.account_id')

    @property
    def image_dest(self):
        """The .jpg file upload destination."""
        ret = self._info['image_dest_pat'].format(self._info)
        return ret

    @property
    def video_dest(self):
        """The .mov file upload destination."""
        ret = self._info['video_dest_pat'].format(self._info)
        return ret

    @property
    def workfile_dest(self):
        """The .mov file upload destination."""
        ret = self._info['workfile_dest_pat'].format(self._info)
        return ret

    def is_my_task(self):
        """Return if shot assined to current account.  """
        return bool(self.current_account_id() == self.artist_id)


class IDError(Exception):
    """Indicate can't specify shot id on cgtw."""

    def __init__(self, *args):
        Exception.__init__(self)
        self.message = args

    def __str__(self):
        return u'Can not found item id:{}'.format(self.message)


class FolderError(Exception):
    """Indicate can't found destination folder."""

    def __init__(self, *args):
        Exception.__init__(self)
        self.message = args

    def __str__(self):
        return u'No such folder on server:{}'.format(self.message)


class LoginError(Exception):
    """Indicate can't found destination folder."""

    def __init__(self, *args):
        Exception.__init__(self)
        self.message = args

    def __str__(self):
        return u'Not loged in.  \n{}'.format(self.message)
