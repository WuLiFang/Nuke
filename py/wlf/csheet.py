# usr/bin/env python
# -*- coding=UTF-8 -*-

import os
import sys
import locale
import argparse
import json
from subprocess import call, Popen, PIPE, STDOUT

import nuke

VERSION = 2.31

sys_codec = locale.getdefaultlocale()[1]
script_codec = 'UTF-8'
nuke_codec = 'UTF-8'

class Contactsheet(object):

    last_output = None
    backdrop_read_node = None
    read_nodes = None
    shot_width, shot_height = 1920, 1080
    contactsheet_shot_width, contactsheet_shot_height = 1920, 1160
    config = {}

    def __init__(self, config):
        self.read_config(config)
        self.image_dir = self.config['csheet_footagedir'].replace('\\', '/')
        self.image_list = self.getImageList(self.image_dir)
        self.read_nodes = []
        self.jpg_output = None
        self.main()

    def read_config(self, config):
        self.config.update(json.loads(config.read()))

    def main(self):

        nuke.Root()['project_directory'].setValue(os.getcwd().replace('\\', '/'))

        self.createReadNodes()
        self.Contactsheet()
        self.createBackdrop()
        self.mergeBackdrop()
        self.modifyShot()
        self.modifyBackdrop()
        #nuke.scriptSave('E:\\temp.nk')
        self.writeJPG()
        return 

    def Contactsheet(self):
        contactsheet_node = nuke.nodes.ContactSheet(inputs=self.read_nodes, width='{rows*shot_format.w+gap*(rows+1)}', height='{columns*shot_format.h+gap*(columns+1)}', rows='{{ceil(pow([inputs this], 0.5))}}', columns='{rows}', gap=50, roworder='TopBottom')
        contactsheet_node.addKnob(nuke.WH_Knob('shot_format'))
        contactsheet_node['shot_format'].setValue([self.contactsheet_shot_width, self.contactsheet_shot_height])
        contactsheet_node.setName('_Csheet')
        self.contactsheet_node = contactsheet_node
        return contactsheet_node
    
    def createReadNodes(self):
        for i in self.image_list:
            file = unicode(os.path.join(self.image_dir ,i).replace('\\', '/').encode(nuke_codec))
            read_node = nuke.nodes.Read(file=file)
            if read_node.hasError():
                nuke.delete(read_node)
                print(u'排除:\t\t\t{} (不能读取)'.format(i))
            else:
                self.read_nodes.append(read_node)

    def createBackdrop(self, image=None):
        if not image:
            image = unicode(self.config['backdrop'])
        if os.path.isfile(image):
            print(u'使用背板:\t\t{}'.format(image))
            read_node = nuke.nodes.Read(file=image.encode('UTF-8').replace('\\', '/'))
            if read_node.hasError():
                self.backdrop_read_node = nuke.nodes.Constant()
                print(u'**警告**\t\t背板文件无法读取,将用纯黑代替')
                return False
            else:
                self.backdrop_read_node = read_node
                return read_node
        else:
            self.backdrop_read_node = nuke.nodes.Constant()
            print(u'**提示**\t\t找不到背板文件,将用纯黑代替')
            return False

    def getImageList(self, dir='images'):
        image_list = list(i.decode(sys_codec).encode(script_codec) for i in os.listdir(dir))

        if not image_list:
            raise FootageError
        
        # Exclude excess image
        mtime = lambda file: os.stat(dir + '\\' + file.decode(script_codec). encode(sys_codec)).st_mtime
        image_list.sort(key=mtime, reverse=True)
        getShotName = lambda file_name : file_name.split('.')[0].rstrip('_proxy').lower()
        shot_list = []
        result = []
        for image in image_list:
            shot = getShotName(image)
            if shot in shot_list:
                print(u'排除:\t\t\t{} (较旧)'.format(image))
            else:
                shot_list.append(shot)
                print(u'包含:\t\t\t{}'.format(image))
                result.append(image)
        result.sort()
        print(u'总计图像数量:\t\t{}'.format(len(image_list)))
        print(u'总计有效图像:\t\t{}'.format(len(result)))
        print(u'总计镜头数量:\t\t{}'.format(len(shot_list)))
        return result
    
    def mergeBackdrop(self):
        merge_node = nuke.nodes.Merge2(inputs=[self.backdrop_read_node, self.contactsheet_node])
        _reformat_backdrop_node = nuke.nodes.Reformat(type='scale', scale='{_Csheet.width/input.width*backdrop_scale}')
        k = nuke.Double_Knob('backdrop_scale', '背板缩放')
        k.setValue(1.13365)
        _reformat_backdrop_node.addKnob(k)
        _reformat_backdrop_node.setName('_Reformat_Backdrop')
        insertNode(_reformat_backdrop_node, self.backdrop_read_node)
        insertNode(nuke.nodes.Transform(translate='{1250*_Reformat_Backdrop.scale} {100*_Reformat_Backdrop.scale}', center='{input.width/2} {input.height/2}'), self.contactsheet_node)
        self.last_output = merge_node
        return merge_node
        
    def modifyShot(self):
        nuke.addFormat('{} {} contactsheet_shot'.format(self.contactsheet_shot_width, self.contactsheet_shot_height))
        for i in self.read_nodes:
            reformat_node = nuke.nodes.Reformat(format='contactsheet_shot',center=False, black_outside=True)
            transform_node = nuke.nodes.Transform(translate='0 {}'.format(self.contactsheet_shot_height-self.shot_height))
            text_node = nuke.nodes.Text2(message='[lrange [split [basename [metadata input/filename]] ._] 3 3]', box='0 0 0 80', color='0.145 0.15 0.14 1')
            insertNode(text_node, i)
            insertNode(transform_node, i)
            insertNode(reformat_node, i)
        
    def modifyBackdrop(self):
        EP = self.config['EP']
        SCENE = self.config['SCENE']
        nuke.addFormat('11520 6480 backdrop')
        reformat_node = nuke.nodes.Reformat(format='backdrop')
        if EP:
            if EP.startswith('EP'):
                ep = EP[2:]
            else:
                ep = EP
            insertNode(nuke.nodes.Text2(message=ep, box='288 6084 1650 6400', xjustify='center', yjustify='center', global_font_scale=3, color='0.155'), self.backdrop_read_node)
        if SCENE:
            insertNode(nuke.nodes.Text2(message=SCENE, box='288 4660 1650 5000', xjustify='center', yjustify='center', global_font_scale=3, color='0.155'), self.backdrop_read_node)
        insertNode(reformat_node, self.backdrop_read_node)
        
    def writeJPG(self):
        file_name = unicode(self.config['csheet']).replace('\\', '/')
        write_node = nuke.nodes.Write(inputs=[self.last_output], file=file_name.encode('UTF-8'), file_type='jpg', _jpeg_quality='1', _jpeg_sub_sampling='4:4:4')
        print(u'输出色板:\t\t{}'.format(file_name))
        nuke.render(write_node, 1, 1)
        self.jpg_output = os.path.abspath(file_name)
        return file_name

def insertNode(node, input_node):
    # Create dot presents input_node 's output
    input_node.selectOnly()
    dot = nuke.createNode('Dot')
    
    # Set node connection
    node.setInput(0, input_node)
    dot.setInput(0, node)
    
    # Delete dot
    nuke.delete(dot)

class FootageError(Exception):
    def __init__(self):
        print(u'\n**错误** - 在images文件夹中没有可用图像\n')

def main():
    args = parse_arg()
    Contactsheet(args.config)

def parse_arg():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('config', metavar='cfg', type=file,
                        help='json config file generated by SceneTool')
    args = parser.parse_args()
    return args

def create_csheet():
    if nuke.Root().modified() or not nuke.value('root.name'):
        return False
    
    json = os.path.join(os.path.dirname(nuke.scriptName()), '.projectsettings.json')
    if os.path.isfile(json):
        cmd = u'START "Csheet" "{NUKE}" -t "{script}" "{json}"'.format(NUKE=nuke.env['ExecutablePath'], script=__file__.rstrip('cd'), json=json)
        call(cmd, shell=True)
    else:
        return False

if __name__ == '__main__':
    try:
        main()
    except SystemExit, e:
        exit(e)
    except:
        import traceback
        traceback.print_exc()