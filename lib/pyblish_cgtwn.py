# -*- coding=UTF-8 -*-
"""CGTeamWork pyblish plug-in.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

import nuke
import pyblish.api

from cgtwn import Task
from node import wlf_write_node
from wlf import cgtwq
from wlf.path import PurePath
from wlf.files import copy

LOGGER = logging.getLogger('wlf.pyblish_cgtwn')

# pylint: disable=no-init


class CollectFile(pyblish.api.ContextPlugin):
    """获取当前Nuke使用的文件.   """

    order = pyblish.api.CollectorOrder
    label = '获取当前文件'

    def process(self, context):
        context.data['comment'] = ''

        assert isinstance(context, pyblish.api.Context)
        filename = nuke.value('root.name')
        if not filename:
            raise ValueError('工程尚未保存.')

        context.data['task'] = Task(PurePath(filename).shot)
        context.create_instance(filename,
                                family='Nuke文件')


class CollectFrameRange(pyblish.api.ContextPlugin):
    """获取当前工程帧范围设置.   """
    label = '获取帧范围'

    def process(self, context):
        first = nuke.numvalue('root.first_frame')
        last = nuke.numvalue('root.last_frame')
        context.create_instance(
            '帧范围: {:.0f}-{:.0f}'.format(first, last),
            first=first,
            last=last,
            family='帧范围')


class CollectFPS(pyblish.api.ContextPlugin):
    """获取当前工程帧速率设置.   """
    label = '获取帧速率'

    def process(self, context):
        fps = nuke.numvalue('root.fps')
        context.create_instance(
            name='帧速率: {:.0f}'.format(fps),
            fps=fps,
            family='帧速率')


class CollectUser(pyblish.api.ContextPlugin):
    """获取当前登录的用户帐号.   """

    order = pyblish.api.CollectorOrder
    label = '获取当前用户'

    def process(self, context):
        name = cgtwq.database.account_name()
        assert isinstance(context, pyblish.api.Context)
        context.create_instance(
            name='制作者: {}'.format(name),
            user=name,
            id=cgtwq.server.account_id(),
            family='制作者')


class VadiateArtist(pyblish.api.InstancePlugin):
    """检查任务是否分配给当前用户。  """

    order = pyblish.api.ValidatorOrder
    label = '制作者检查'
    families = ['制作者']

    def process(self, instance):
        assert isinstance(instance, pyblish.api.Instance)
        task = instance.context.data['task']
        assert isinstance(task, Task)
        current_id = instance.data['id']
        task_account_id = task['account_id'][0]
        LOGGER.debug(task_account_id)

        for i in task_account_id:
            if current_id in i.split(','):
                return
        LOGGER.error('用户不匹配: %s -> %s',
                     instance.data['user'], task['artist'][0])
        raise cgtwq.AccountError(
            owner=task_account_id, current=current_id)


class VadiateFrameRange(pyblish.api.InstancePlugin):
    """检查帧范围是否匹配上游.  """

    order = pyblish.api.ValidatorOrder
    label = '帧范围检查'
    families = ['帧范围']

    def process(self, instance):
        assert isinstance(instance, pyblish.api.Instance)
        task = instance.context.data['task']
        assert isinstance(task, Task)

        n = task.import_video('animation_videos')
        upstream_framecount = int(n['last'].value() - n['first'].value() + 1)
        current_framecount = instance.data['last'] - instance.data['first'] + 1
        if upstream_framecount != current_framecount:
            LOGGER.error('工程帧数和上游不一致: %s -> %s',
                         current_framecount, upstream_framecount)
            raise ValueError(
                'Frame range not match.',
                upstream_framecount,
                current_framecount)


class VadiateFPS(pyblish.api.InstancePlugin):
    """检查帧速率是否匹配数据库设置.   """

    order = pyblish.api.ValidatorOrder
    label = '检查帧速率'
    families = ['帧速率']

    def process(self, instance):
        task = instance.context.data['task']
        assert isinstance(task, Task)
        database = task.module.database
        fps = database.get_data('fps', is_user=False)
        if not fps:
            LOGGER.warning('数据库未设置帧速率: %s', database.name)
        else:
            current_fps = instance.data['fps']
            if float(fps) != current_fps:
                LOGGER.error('帧速率不一致: %s -> %s', current_fps, fps)
                raise ValueError('Not same fps', fps, current_fps)


class ExtractJPG(pyblish.api.InstancePlugin):
    """生成单帧图.   """

    order = pyblish.api.ExtractorOrder
    label = '生成JPG'
    families = ['Nuke文件']

    def process(self, instance):
        n = wlf_write_node()
        if n:
            LOGGER.debug('render_jpg: %s', n.name())
            try:
                n['bt_render_JPG'].execute()
            except RuntimeError as ex:
                nuke.message(str(ex))
        else:
            LOGGER.warning('工程中缺少wlf_Write节点')


class UploadWorkFile(pyblish.api.InstancePlugin):
    """上传工作文件至CGTeamWork.   """

    order = pyblish.api.IntegratorOrder
    label = '上传工作文件'
    families = ['Nuke文件']

    def process(self, instance):
        assert isinstance(instance, pyblish.api.Instance)
        workfile = instance.data['name']
        task = instance.context.data['task']
        assert isinstance(task, Task)
        dest = task.get_filebox('workfile').path + '/'
        dest = 'E:/test_pyblish/'

        copy(workfile, dest)


class UploadJPG(pyblish.api.InstancePlugin):
    """上传工作单帧至CGTeamWork.   """

    order = pyblish.api.IntegratorOrder
    label = '上传单帧'
    families = ['Nuke文件']

    def process(self, instance):
        task = instance.context.data['task']
        assert isinstance(task, Task)

        n = wlf_write_node()
        path = nuke.filename(n.node('Write_JPG_1'))
        dest = task.get_filebox('image').path + '/'
        dest = 'E:/test_pyblish/'
        copy(path, dest)
