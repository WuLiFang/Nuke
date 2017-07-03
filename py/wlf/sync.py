# usr/bin/env python
# -*- coding=UTF-8 -*-

import os
import locale
from config import Config
from subprocess import call

sys_codec = locale.getdefaultlocale()[1]

def copy(src, dst):
    cmd = u'XCOPY /Y /V "{}" "{}"'.format(unicode(src), unicode(dst)).encode(sys_codec)
    call(cmd)

class Sync(Config):

    def getFileList(self):
        cfg = self.config
        image_dir = cfg['IMAGE_FNAME']
        video_dir = cfg['VIDEO_FNAME']
        if os.path.exists(image_dir):
            cfg['image_list'] = list(i for i in os.listdir(image_dir) if i.endswith('.jpg'))
        else:
            cfg['image_list'] = []
        if os.path.exists(video_dir):
            cfg['video_list'] = list(i for i in os.listdir(video_dir) if i.endswith('.mov'))
        else:
            cfg['video_list'] = []
        self.getIgnoreList()
        self.updateConfig()
            
    def getIgnoreList(self):
        cfg = self.config
        cfg['ignore_list'] = []

        if cfg['isVideoUp']:
            video_list = list(cfg['video_list'])
            for i in video_list:
                src = os.path.join(cfg['VIDEO_FNAME'], i)
                dst = os.path.join(cfg['video_dest'], i)
                if os.path.exists(dst) and os.path.getmtime(src) == os.path.getmtime(dst):
                    cfg['ignore_list'].append(i)
                    cfg['video_list'].remove(i)

        if cfg['isImageUp']:
            image_list = list(cfg['image_list'])
            for i in image_list:
                src = os.path.join(cfg['IMAGE_FNAME'], i)
                dst = os.path.join(cfg['image_dest'], i)
                if os.path.exists(dst) and os.path.getmtime(src) <= os.path.getmtime(dst):
                    cfg['ignore_list'].append(i)
                    cfg['image_list'].remove(i)

    def uploadVideos(self):
        cfg = self.config
        video_dest = unicode(cfg['video_dest'])

        if os.path.exists(os.path.dirname(video_dest)):
            if not os.path.exists(video_dest):
                os.mkdir(video_dest)
        else:
            print(u'**错误** 视频上传文件夹不存在, 将不会上传。')
            return False

        for i in cfg['video_list']:
            src = os.path.join(cfg['VIDEO_FNAME'], i)
            dst = video_dest
            copy(src, dst)

    def downloadVideos():
        pass

    def uploadImages(self):
        cfg = self.config
        dest = unicode(cfg['image_dest'])
        if os.path.exists(os.path.dirname(dest)):
            if not os.path.exists(dest):
                os.mkdir(dest)
        else:
            print(u'**错误** 图片上传文件夹不存在, 将不会上传。')
            return False

        for i in cfg['image_list']:
            src = os.path.join(cfg['IMAGE_FNAME'], i)
            dst = dest
            copy(src, dst)

    def downloadImages(self):
        cfg = self.config
        src = cfg['image_dest']
        dst = cfg['IMAGE_FNAME']
        print(u'## 下载单帧: {} -> {}'.format(src, dst))
        call(' '.join(['XCOPY', '/Y', '/D', '/I', '/V', src, dst]))

    def uploadCSheet(self):
        dest = self.config['csheet_dest']

        if not os.path.exists(os.path.dirname(dest)):
            return False
            print(u'**错误** 色板上传文件夹不存在, 将不会上传。')

        if not os.path.exists(dest):
            os.mkdir(dest)

        copy(self.config['csheet'], dest)