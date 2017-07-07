#! usr/bin/env python
# -*- coding=UTF-8 -*-
"""
cgteamwork integration with nuke.
"""
import os
import sys
import locale
import shutil
import re
from subprocess import call

import nuke
CGTW_PATH = r"C:\cgteamwork\bin\base"
if os.path.exists(CGTW_PATH):
    sys.path.append(CGTW_PATH)
    import cgtw
else:
    nuke.error('CGTeamWork not found: {}'.format(CGTW_PATH))


VERSION = '0.2.1'
SYS_CODEC = locale.getdefaultlocale()[1]

def copy(src, dst):
    dst_dir = os.path.dirname(dst)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    shutil.copy2(src, dst)
    print(u'{} -> {}'.format(src, dst))

class CGTeamWork(object):
    database = u'proj_qqfc_2017'

    def __init__(self):
        self._tw = cgtw.tw()

    def is_login(self):
        ret = self._tw.sys().get_socket_status()
        return ret
        
    def check_login(self):
        if not self.is_login():
            raise LoginError

    @classmethod
    def set_database(cls, database):
        cls.database = database

    @classmethod
    def ask_database(cls):
        database = nuke.getInput(u'工程英文名称'.encode('UTF-8'), cls.database)
        if database:
            cls.set_database(database)


class Shot(CGTeamWork):
    pipeline = u'合成'
    pipeline_name = u'comp'
    module = u'shot_task'
    work_folder = u'work'
    shot_task_folder = u'shot_work'
    image_folder = u'Image'
    server = u'Z:\\CGteamwork_Test'

    def __init__(self):
        super(Shot, self).__init__()

        self._task_module = self._tw.task_module(self.database, self.module)

        self._name = self.get_name()
        self._id = self.get_id()
        self._path = self.get_path()

        self._task_module.init_with_id(self._id)

    def get_name(self):
        ret = nuke.value('root.name', '')
        ret = os.path.basename(ret)
        ret = os.path.splitext(ret)[0]
        ret = re.sub(r'_v\d+$', '', ret)
        return ret
    
    def get_id(self):
        self.check_login()

        id_list = self._task_module.get_with_filter([], [['shot.shot', '=', self._name], ['shot_task.pipeline', '=', self.pipeline]])
        if not id_list:
            raise IDError(self.database, self.module, self.pipeline, self._name)
        elif len(id_list) is not 1:
            raise IDError(u'多个符合的条目'.encode('UTF-8'), id_list)
        ret = id_list[0]['id']
        return ret

    def get_path(self):
        self.check_login()
    
    def get_workfile_dest(self):
        infos = self._task_module.get(['shot.shot', 'eps.project_code', 'eps.eps_name'])[0]
        ret = os.path.join(self.server, infos['eps.project_code'], self.module, self.pipeline_name, infos['eps.eps_name'], infos['shot.shot'], self.work_folder) + '\\'
        return ret

    def get_image_dest(self):
        infos = self._task_module.get(['shot.shot', 'eps.project_code', 'eps.eps_name'])[0]
        ret = os.path.join(self.server, infos['eps.project_code'], self.shot_task_folder, self.pipeline_name, infos['eps.eps_name'], infos['shot.shot'], self.image_folder, infos['shot.shot'] + '.jpg')
        if not os.path.isdir(os.path.dirname(ret)):
            raise FolderError(ret)
        return ret

    def upload_nk_file(self):
        src = os.path.normcase(nuke.scriptName())
        dst = self.get_workfile_dest()
        copy(src, dst)
        self.add_note(u'[log]上传nk文件: {}'.format(os.path.basename(src)))

    def upload_image(self):
        n = nuke.toNode('_Write') or nuke.toNode('wlf_Write1') or nuke.allNodes('wlf_Write')
        if isinstance(n, list):
            n = n[0]
        w = n.node('Write_JPG_1')
        if w:
            src = os.path.join(nuke.value('root.project_directory', ''), nuke.filename(w))
            dst = self.get_image_dest()
            if os.path.exists(dst) and (os.path.getmtime(src) - os.path.getmtime(dst) < 1e-06):
                nuke.message('无需上传')
                return None
            else:
                copy(src, dst)
                self.add_note(u'[log]上传单帧: {}'.format(os.path.basename(src)))
                nuke.message('上传完毕')
                return dst
        else:
            return False

    def add_note(self, s):
        self._task_module.create_note(s)
            
    def ask_add_note(self):
        self.check_login()
        s = nuke.getInput(u'note内容'.encode('UTF-8'), u'来自nuke的note'.encode('UTF-8'))
        if s:
            self.add_note(s)

class IDError(Exception):
    def __init__(self, *args):
        self.message = args

    def __str__(self):
        return '找不到对应条目:{}'.format(self.message)

class FolderError(Exception):
    def __init__(self, *args):
        self.message = args

    def __str__(self):
        return '服务器上无对应文件夹:{}'.format(self.message)


class LoginError(Exception):
    def __str__(self):
        return 'CGTeamWork服务器未连接'
        