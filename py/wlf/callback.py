# -*- coding: UTF-8 -*-
import os
import locale

import nuke
import nukescripts

import edit
import csheet
import asset
import pref
import ui
import cgtw


SYS_CODEC = locale.getdefaultlocale()[1]


def init():
    nuke.addBeforeRender(create_out_dirs, nodeClass='Write')


def menu():
    _dropframe()
    _cgtw()
    add_dropdata_callback()
    nuke.addOnUserCreate(_gizmo_to_group_on_create)
    nuke.addOnCreate(lambda: edit.randomGlColor(nuke.thisNode()))
    nuke.addUpdateUI(_gizmo_to_group_update_ui)
    nuke.addUpdateUI(_autoplace)
    nuke.addOnScriptSave(edit.enableRSMB, kwargs={'prefix': '_'})
    nuke.addOnScriptSave(_check_project)
    nuke.addOnScriptSave(_lock_connections)
    nuke.addOnScriptSave(_jump_frame)
    nuke.addOnScriptClose(_create_csheet)
    nuke.addOnScriptClose(_render_jpg)
    nuke.addOnScriptClose(_send_to_render_dir)
    nuke.addAutolabel(ui.custom_autolabel)


def _cgtw():
    def on_close_callback():
        if nuke.modified():
            return False

        if os.path.basename(nuke.value('root.name')).startswith('SNJYW'):
            cgtw.Shot().upload_image()

    nuke.addOnScriptClose(on_close_callback)

def _dropframe():
    nuke.addUpdateUI(lambda : asset.DropFrameCheck(nuke.thisNode()).start(), nodeClass='Read')
    nuke.addOnScriptSave(asset.DropFrameCheck.show_dialog)

def _create_csheet():
    if nuke.numvalue('preferences.wlf_create_csheet', 0.0):
        if not nuke.modified() and nuke.value('root.name'):
            csheet.ContactSheetThread().run(new_process=True)

def _check_project():
    if not nuke.value('root.project_directory'):
        nuke.message('工程目录未设置')

def _lock_connections():
    if nuke.numvalue('preferences.wlf_lock_connections', 0.0):
        nuke.Root()['lock_connections'].setValue(1);
        nuke.Root().setModified(False)

def _jump_frame():
    if nuke.numvalue('preferences.wlf_lock_connection', 0.0) and nuke.exists('_Write.knob.frame'):
        nuke.frame(nuke.numvalue('_Write.knob.frame'));
        nuke.Root().setModified(False)

def _send_to_render_dir():
    if nuke.modified():
        return False
    
    if nuke.numvalue('preferences.wlf_send_to_dir', 0.0):
        asset.sent_to_dir(nuke.value('preferences.wlf_render_dir'))

def _render_jpg():
    if nuke.modified():
        return False

    if nuke.numvalue('preferences.wlf_send_to_dir', 0.0) and nuke.exists('_Write.bt_render_JPG'):
        nuke.toNode('_Write')['bt_render_JPG'].execute()
        
def _gizmo_to_group_on_create():
    n = nuke.thisNode()
    if not nuke.numvalue('preferences.wlf_gizmo_to_group', 0.0):
        return

    if not isinstance(n, nuke.Gizmo):
        return

    # Avoid scripted gizmo.
    if nuke.knobChangeds.get(n.Class()):
        return

    n.addKnob(nuke.Text_Knob('wlf_gizmo_to_group'))

def _gizmo_to_group_update_ui():
    n = nuke.thisNode()
    _temp_knob_name = 'wlf_gizmo_to_group'
    _has_temp_knob = nuke.exists('{}.{}'.format(n.name(), _temp_knob_name))

    if _has_temp_knob:
        n = edit.gizmo_to_group(n)
        n.removeKnob(n[_temp_knob_name])
        n.removeKnob(n['User'])

def _autoplace():
    if nuke.numvalue('preferences.wlf_autoplace', 0.0):
        nuke.autoplace(nuke.thisNode())

def _print_name():
    print(nuke.thisNode().name())
    

def create_out_dirs():
    trgDir = os.path.dirname( nuke.filename( nuke.thisNode() ) )
    if not os.path.isdir( trgDir ):
        os.makedirs( trgDir )

def add_dropdata_callback():
    def _db(type, data):
        if type == 'text/plain' and os.path.basename(data).lower() == 'thumbs.db':
            return True
        else:
            return None

    def _fbx(type, data):
        if type == 'text/plain' and data.endswith('.fbx'):
            camera_node = nuke.createNode('Camera2', 'read_from_file True file {data} frame_rate 25 suppress_dialog True label {{导入的摄像机：\n[basename [value file]]\n注意选择file -> node name}}'.format(data=data))
            camera_node.setName('Camera_3DEnv_1')
            return True
        else:
            return None

    def _vf(type, data):
        if type == 'text/plain' and data.endswith('.vf'):
            vectorfield_node = nuke.createNode('Vectorfield', 'vfield_file "{data}" file_type vf label {{[value this.vfield_file]}}'.format(data=data))
            return True
        else:
            return None
            
    def _else(type, data):
        if type == 'text/plain':
            if data.startswith('file:///Y:'):
                data = data[8:]
                print(data)
            nuke.createNode('Read', 'file "{}"'.format(data))
            return True
        else:
            return None
            
    def _dir(type, data):
        def _file(type, data):
            _db(type, data)
            _fbx(type, data)
            _vf(type, data)
            _else(type, data)
            
        def _path(type, data):
            if os.path.isdir(data):
                _dir(type, data)
                return True
            else:
                _file(type, data)
                return True

        if type == 'text/plain' and os.path.isdir(data):
            _dirname = data.replace('\\', '/')
            for i in nuke.getFileNameList(_dirname):
                _path(type, '/'.join([_dirname, i]))
            return True
        else:
            return None


    nukescripts.addDropDataCallback(_fbx)
    nukescripts.addDropDataCallback(_vf)
    nukescripts.addDropDataCallback(_db)
    nukescripts.addDropDataCallback(_else)
    nukescripts.addDropDataCallback(_dir)
    
    def _catch_all(type, data):
        print(type)
        print(data)
        return None
        
    # nukescripts.addDropDataCallback(_catch_all)
    # nuke.addOnScriptLoad(SNJYW.setProjectRoot)
    # nuke.addOnScriptLoad(SNJYW.setRootFormat)