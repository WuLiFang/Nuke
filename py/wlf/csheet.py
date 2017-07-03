# -*- coding=UTF-8 -*-

import os
import sys
import locale
import json
import threading
from subprocess import call, Popen, PIPE, STDOUT

import nuke


SYS_CODEC = locale.getdefaultlocale()[1]


class ContactSheet(object):
    shot_width, shot_height = 1920, 1080
    contactsheet_shot_width, contactsheet_shot_height = 1920, 1160

    def __init__(self, config=None):
        self.read_config()
        nuke.scriptClear()
        nuke.Root()['project_directory'].setValue(os.getcwd().replace('\\', '/'))
        self.create_nodes()
        self.output()

    def read_config(self):
        with open(self.json_path()) as f:
            self._config = json.load(f)

    def json_path(self):
        if __name__ == '__main__':
            return sys.argv[1]
        else:
            return os.path.join(os.path.dirname(nuke.value('root.name')), '.projectsettings.json')

    def create_nodes(self):
        nuke.addFormat('{} {} contactsheet_shot'.format(self.contactsheet_shot_width, self.contactsheet_shot_height))
        _nodes = []
        for i in self.image_list():
            n = nuke.nodes.Read(file=i.replace('\\', '/').encode('UTF-8'))
            if n.hasError():
                nuke.delete(n)
                print(u'排除:\t\t\t{} (不能读取)'.format(i))
                continue
            n = nuke.nodes.Reformat(
                inputs=[n],
                format='contactsheet_shot',
                center=False,
                black_outside=True
            )
            n = nuke.nodes.Transform(
                inputs=[n],
                translate='0 {}'.format(self.contactsheet_shot_height-self.shot_height)
            )
            n = nuke.nodes.Text2(
                inputs=[n],
                message='[lrange [split [basename [metadata input/filename]] ._] 3 3]',
                box='0 0 0 80',
                color='0.145 0.15 0.14 1'
            )
            _nodes.append(n)

        n = nuke.nodes.ContactSheet(
            inputs=_nodes,
            width='{rows*shot_format.w+gap*(rows+1)}',
            height='{columns*shot_format.h+gap*(columns+1)}',
            rows='{{ceil(pow([inputs this], 0.5))}}',
            columns='{rows}',
            gap=50,
            roworder='TopBottom')
        n.setName('_Csheet')
        k = nuke.WH_Knob('shot_format')
        k.setValue([self.contactsheet_shot_width, self.contactsheet_shot_height])
        n.addKnob(k)
        _contactsheet_node = n

        if os.path.isfile(self._config['backdrop'].encode(SYS_CODEC)):
            print(u'使用背板:\t\t{}'.format(self._config['backdrop']))
            n = nuke.nodes.Read()
            n['file'].fromUserText(self._config['backdrop'].encode('UTF-8'))
            if n.hasError():
                n = nuke.nodes.Constant()
                print(u'**警告**\t\t背板文件无法读取,将用纯黑代替')
        else:
            n = nuke.nodes.Constant()
            print(u'**提示**\t\t找不到背板文件,将用纯黑代替')
        n = nuke.nodes.Reformat(
            inputs=[n],
            type='scale',
            scale='{_Csheet.width/input.width*backdrop_scale}'
        )
        n.setName('_Reformat_Backdrop')
        k = nuke.Double_Knob('backdrop_scale', '背板缩放')
        k.setValue(1.13365)
        n.addKnob(k)
        _reformat_node = n
        n = nuke.nodes.Transform(
            inputs=[_contactsheet_node],
            translate='{1250*_Reformat_Backdrop.scale} {100*_Reformat_Backdrop.scale}',
            center='{input.width/2} {input.height/2}'
        )
        _transform_node = n
        n = nuke.nodes.Merge2(inputs=[_reformat_node, _transform_node])
        n = nuke.nodes.Write(
            inputs=[n],
            file=self._config['csheet'].encode('UTF-8').replace('\\', '/'),
            file_type='jpg',
            _jpeg_quality='1',
            _jpeg_sub_sampling='4:4:4'
        )
        self._write_node = n

    def output(self):
        #nuke.scriptSave('E:\\temp.nk')
        print(u'输出色板:\t\t{}'.format(self._config['csheet']))
        nuke.render(self._write_node, 1, 1)

    def image_list(self):
        _dir = self._config['csheet_footagedir']
        _images = list(os.path.join(_dir, i.decode(SYS_CODEC)) for i in os.listdir(_dir))

        if not _images:
            raise FootageError
        
        _images.sort(key=lambda file: os.stat(file.encode(SYS_CODEC)).st_mtime, reverse=True)
        _shots = []
        _ret = []
        for image in _images:
            _shot = image.split('.')[0].rstrip('_proxy').lower()
            if _shot in _shots:
                print(u'排除:\t\t\t{} (较旧)'.format(image))
            else:
                print(u'包含:\t\t\t{}'.format(image))
                _shots.append(_shot)
                _ret.append(image)
        _ret.sort()
        print(u'总计图像数量:\t\t{}'.format(len(_images)))
        print(u'总计有效图像:\t\t{}'.format(len(_ret)))
        print(u'总计镜头数量:\t\t{}'.format(len(_shots)))
        return _ret


class ContactSheetThread(threading.Thread, ContactSheet):
    lock = threading.Lock()
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self, new_process=False):
        _json = self.json_path()
        if not os.path.isfile(_json):
            return
        self.lock.acquire()
        _task = nuke.ProgressTask('生成色板')
        _task.setProgress(50)
        _cmd = u'"{NUKE}" -t "{script}" "{json}"'.format(
            NUKE=nuke.EXE_PATH,
            script=__file__.rstrip('cd'),
            json=_json
        )
        if new_process: 
            _cmd = ''.join([u'START "生成色板" ', _cmd])
        call(_cmd.encode(SYS_CODEC), shell=new_process)
        _task.setProgress(100)
        self.lock.release()


class FootageError(Exception):
    def __init__(self):
        print(u'\n**错误** - 在images文件夹中没有可用图像\n')


def main():
    reload(sys)
    sys.setdefaultencoding('UTF-8')

    ContactSheet()

    
if __name__ == '__main__':
    try:
        main()
    except SystemExit, e:
        exit(e)
    except:
        import traceback
        traceback.print_exc()