# -*- coding=UTF-8 -*-
"""CGTeamWork pyblish plug-in.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
from collections import namedtuple

import nuke
import pendulum
import pyblish.api

from node import wlf_write_node
from wlf.files import copy

FootageInfo = namedtuple('FootageInfo', ('filename', 'mtime'))

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

        context.create_instance(filename,
                                family='Nuke文件')


class CollectFrameRange(pyblish.api.ContextPlugin):
    """获取当前工程帧范围设置.   """

    order = pyblish.api.CollectorOrder
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

    order = pyblish.api.CollectorOrder
    label = '获取帧速率'

    def process(self, context):
        fps = nuke.numvalue('root.fps')
        context.create_instance(
            name='帧速率: {:.0f}'.format(fps),
            fps=fps,
            family='帧速率')


class CollectMTime(pyblish.api.ContextPlugin):
    """获取当前工程使用的素材.   """

    order = pyblish.api.CollectorOrder
    label = '获取素材'

    def process(self, context):
        assert isinstance(context, pyblish.api.Context)
        footages = set()
        root = nuke.Root()
        for n in nuke.allNodes('Read', nuke.Root()):
            if n.hasError():
                self.log.warning('读取节点出错: %s', n.name())
                continue
            filename = n.metadata('input/filename')
            mtime = n.metadata('input/mtime')
            if not filename or not mtime:
                continue

            footage = FootageInfo(filename=filename,
                                  mtime=pendulum.from_format(mtime,
                                                             '%Y-%m-%d %H:%M:%S',
                                                             tz='Asia/Shanghai'))
            footages.add(footage)
        instance = context.create_instance(
            '{}个 素材'.format(len(footages)),
            filename=root['name'].value(),
            family='素材')
        instance.extend(footages)


class ValidateMTime(pyblish.api.InstancePlugin):
    """检查素材是否在文件保存之后更改过.   """

    order = pyblish.api.ValidatorOrder
    label = '检查素材修改日期'
    families = ['素材']

    def process(self, instance):
        try:
            filemtime = os.path.getmtime(instance.data['filename'])
        except OSError:
            # Maybe using `Save as`
            return
        filemtime = pendulum.from_timestamp(filemtime)
        is_ok = True
        for i in instance:
            assert isinstance(i, FootageInfo)
            if i.mtime > filemtime:
                self.log.debug('%s > %s', i.mtime, filemtime)
                self.log.warning('新素材: %s: %s', i.filename,
                                 i.mtime.diff_for_humans(locale='zh'))
                is_ok = False
        if not is_ok:
            raise ValueError('Footage newer than comp.')


class ExtractJPG(pyblish.api.InstancePlugin):
    """生成单帧图.   """

    order = pyblish.api.ExtractorOrder
    label = '生成JPG'
    families = ['Nuke文件']

    def process(self, instance):
        if not nuke.numvalue('preferences.wlf_render_jpg', 0.0):
            self.log.info('因首选项而跳过生成JPG')
            return

        n = wlf_write_node()
        if n:
            self.log.debug('render_jpg: %s', n.name())
            try:
                n['bt_render_JPG'].execute()
            except RuntimeError as ex:
                nuke.message(str(ex))
        else:
            self.log.warning('工程中缺少wlf_Write节点')


class SendToRenderDir(pyblish.api.InstancePlugin):
    """发送Nuke文件至渲染文件夹.   """

    order = pyblish.api.IntegratorOrder
    label = '发送至渲染文件夹'
    families = ['Nuke文件']

    def process(self, instance):
        filename = instance.data['name']
        if nuke.numvalue('preferences.wlf_send_to_dir', 0.0):
            render_dir = nuke.value('preferences.wlf_render_dir')
            copy(filename, render_dir + '/')
        else:
            self.log.info('因为首选项设置而跳过')
