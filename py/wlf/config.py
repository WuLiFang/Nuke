# usr/bin/env python
# -*- coding=UTF-8 -*-

import os, sys
import json
import time
import re

class Config(object):
    config = {
                'SERVER': r'\\192.168.1.7\z', 
                'SIMAGE_FOLDER': r'Comp\image', 
                'SVIDEO_FOLDER': r'Comp\mov', 
                'NUKE': r'C:\Program Files\Nuke10.0v4\Nuke10.0.exe', 
                'DIR': 'N:\\', 
                'PROJECT': 'SNJYW', 
                'EP': '', 
                'SCENE': '', 
                'CSHEET_FFNAME': 'images', 
                'CSHEET_PREFIX': 'Contactsheet', 
                'VIDEO_FNAME': 'mov', 
                'IMAGE_FNAME': 'images', 
                'isImageUp': 2, 
                'isImageDown': 2, 
                'isVideoUp': 2, 
                'isVideoDown': 0, 
                'isCSheetUp': 0, 
                'isCSheetOpen': 2, 
                'csheet': '',
                'BACKDROP_DIR': '',
                'backdrop_name': '',
                'image_list': [],
                'video_list': [],
                'ignore_list': [],
                'csheet_footagedir': '',
             }
    cfgfile_path = os.path.join(os.getenv('UserProfile'), 'SceneTools_WLF.json')
    psetting_bname = '.projectsettings.json'

    def __init__(self):
        self.readConfig()            
        self.updateConfig()
            
    def updateConfig(self):
        self.setSyncPath()
        self.setCSheetPath()
        self.setBackDropPath()
        with open(self.cfgfile_path, 'w') as file:
            json.dump(self.config, file, indent=4, sort_keys=True)
    
    def readConfig(self):
        if os.path.exists(self.cfgfile_path):
            with open(self.cfgfile_path) as file:
                last_config = file.read()
            if last_config:
                self.config.update(json.loads(last_config))

    def readProjectSettings(self):
        if os.path.exists(self.psetting_bname):
            with open(self.psetting_bname) as file:
                last_config = file.read()
            if last_config:
                self.config.update(json.loads(last_config))
                
    def updateProjectSettings(self):
        if not os.path.exists(self.psetting_bname):
            self.setConfigByDir()
        try:
            with open(self.psetting_bname, 'w') as file:
                settings = ['PROJECT', 'EP', 'SCENE', 'VIDEO_FNAME', 'IMAGE_FNAME', 'backdrop_name', 'csheet_footagedir', 'backdrop', 'csheet']
                psettings = {}
                for i in settings:
                    psettings[i] = self.config[i]
                json.dump(psettings, file, indent=4, sort_keys=True)
        except IOError as e:
            pass

    def editConfig(self, key, value):
        #print(u'设置{}: {}'.format(key, value))
        self.config[key] = value
        self.updateConfig()
        self.updateProjectSettings()

    def setSyncPath(self):
        cfg = self.config
        cfg['csheet_dest'] = os.path.join(cfg['SERVER'], cfg['PROJECT'], cfg['SIMAGE_FOLDER'], time.strftime('%m%d'))
        cfg['image_dest'] = os.path.join(cfg['SERVER'], cfg['PROJECT'], cfg['SIMAGE_FOLDER'], cfg['EP'], cfg['SCENE'])
        cfg['video_dest'] = os.path.join(cfg['SERVER'], cfg['PROJECT'], cfg['SVIDEO_FOLDER'], cfg['EP'], cfg['SCENE'])

    def setCSheetPath(self):
        cfg = self.config

        cfg['csheet_name'] = cfg['CSHEET_PREFIX'] + ('_{}_{}.jpg'.format(cfg['EP'], cfg['SCENE']) if cfg['EP'] and cfg['SCENE'] else '_{}.jpg'.format(time.strftime('%y%m%d_%H%M')))
        cfg['csheet'] = os.path.join(cfg['DIR'], cfg['csheet_name'])
        cfg['csheet_dest'] = os.path.join(cfg['SERVER'], cfg['PROJECT'], cfg['SIMAGE_FOLDER'], time.strftime('%m%d'))
        cfg['csheet_footagedir'] = os.path.join(cfg['DIR'], cfg['CSHEET_FFNAME'])

    def setBackDropPath(self):
        cfg = self.config
        cfg['backdrop'] = os.path.join(cfg['BACKDROP_DIR'], cfg['backdrop_name'])
        
    def setConfigByDir(self):
        cfg = self.config
        pat = re.compile(r'.*\\(ep.*?)\\.*\\(.+)', flags=re.I)
        match = pat.match(cfg['DIR'])
        if match:
            cfg['EP'], cfg['SCENE'] = match.groups()
