# -*- coding=UTF-8 -*-
"""CGTeamWork pyblish plug-in.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

import nuke
import pyblish.api

from cgtwn import CurrentShot, Task
from edit import CurrentViewer
from node import Last
from nuketools import utf8
from wlf import cgtwq
from wlf.path import PurePath

LOGGER = logging.getLogger('wlf.pyblish_cgtwn')


class CollectFile(pyblish.api.ContextPlugin):
    """获取当前Nuke使用的文件.   """

    order = pyblish.api.CollectorOrder
    label = '当前文件'

    def process(self, context):
        assert isinstance(context, pyblish.api.Context)
        filename = nuke.value('root.name')
        if not filename:
            LOGGER.error('工程尚未保存')
            raise ValueError('Comp not saved yet.')
        instance = context.create_instance(filename)
        instance.data['family'] = 'Nuke文件'
        instance.append(filename)
        context.data['task'] = Task(PurePath(filename).shot)

        first = nuke.numvalue('root.first_frame')
        last = nuke.numvalue('root.last_frame')
        instance = context.create_instance(
            '帧范围 {:.0f}-{:.0f}'.format(first, last))
        instance.data['family'] = '帧范围'
        instance.data['first'] = first
        instance.data['last'] = last


class VadiateArtist(pyblish.api.InstancePlugin):
    """检查任务是否分配给当前用户。  """

    order = pyblish.api.ValidatorOrder
    label = '制作者检查'
    families = ['Nuke文件']

    def process(self, instance):
        assert isinstance(instance, pyblish.api.Instance)
        task = instance.context.data['task']
        assert isinstance(task, Task)
        current_account_id = cgtwq.server.account_id()
        task_account_id = task['account_id']
        LOGGER.debug(task_account_id)

        for i in task_account_id:
            if current_account_id in i.split(','):
                return

        raise cgtwq.AccountError(
            owner=task_account_id, current=current_account_id)


class VadiateFrameRange(pyblish.api.InstancePlugin):
    """检查帧范围是否匹配上游.  """

    order = pyblish.api.ValidatorOrder
    label = '帧范围检查'
    families = ['帧范围']

    def process(self, instance):
        assert isinstance(instance, pyblish.api.Instance)
        nodes = {
            '动画视频': 'animation'
        }
        root = nuke.Root()
        msg = []
        first = instance.data['first']
        last = instance.data['last']
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
            n['frame_mode'].setValue(b'start_at')
            n['frame'].setValue(unicode(first).encode('utf-8'))
            CurrentViewer().link(n, input_num, replace=False)
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
            raise ValueError(msg)
        elif not has_video_node:
            if current['fps'] != default_fps:
                confirm = nuke.ask(utf8(
                    '当前fps: {}, 设为默认值: {} ?'.format(current['fps'], default_fps)))
                if confirm:
                    nuke.knob('root.fps', utf8(default_fps))


class ExtractJPG(pyblish.api.InstancePlugin):
    order = pyblish.api.ExtractorOrder
    label = '生成JPG'

    def process(self, instance):
        pass


class UploadWorkFile(pyblish.api.InstancePlugin):
    order = pyblish.api.IntegratorOrder
    label = '上传工作文件'
    families = ['Nuke文件']

    def process(self, instance):
        pass


class UploadJPG(pyblish.api.InstancePlugin):
    order = pyblish.api.IntegratorOrder
    label = '上传单帧'

    def process(self, instance):
        pass
