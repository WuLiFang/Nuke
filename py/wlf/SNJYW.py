# -*- coding:UTF-8 -*-

import nuke
import os

project_prefix = 'SNJYW_'

def setProjectRoot(path='N:'):
    try:
        scriptName = os.path.basename(nuke.scriptName()).split('.')[0]
        splited_script_name = scriptName.split('_')
        project = splited_script_name[0]
        ep = splited_script_name[1]
        scene = splited_script_name[2]
    except IndexError:
        return False
    if scriptName.startswith(project_prefix):
        nuke.root()['project_directory'].setValue(path + '/' + project + '/Shots/' + ep + '/Comp/Working/' + scene)
        
def setRootFormat():
    if os.path.basename(nuke.scriptName()).startswith(project_prefix):
        nuke.Root()['fps'].setValue(25)
        nuke.Root()['format'].setValue('HD_1080')