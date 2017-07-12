# -*- coding: UTF-8 -*-
"""Add callback for wlf plugins."""

import locale
import os

import nuke
import nukescripts

from . import asset, cgtwn, csheet, edit, ui

SYS_CODEC = locale.getdefaultlocale()[1]


def init():
    """Add callback for nuke init phase."""

    nuke.addBeforeRender(create_out_dirs, nodeClass='Write')


def menu():
    """Add callback for nuke menu phase."""
    def _dropframe():
        nuke.addOnUserCreate(lambda: asset.DropFrameCheck(
            nuke.thisNode()).start(), nodeClass='Read')
        nuke.addOnScriptSave(asset.DropFrameCheck.show_dialog)

    add_dropdata_callback()
    nuke.addOnUserCreate(_gizmo_to_group_on_create)
    nuke.addOnUserCreate(lambda: edit.set_random_glcolor(nuke.thisNode()))
    nuke.addUpdateUI(_gizmo_to_group_update_ui)
    nuke.addUpdateUI(_autoplace)
    nuke.addOnScriptSave(edit.enable_rsmb, kwargs={'prefix': '_'})
    nuke.addOnScriptSave(_check_project)
    nuke.addOnScriptSave(_check_fps)
    nuke.addOnScriptSave(_lock_connections)
    nuke.addOnScriptSave(_jump_frame)
    nuke.addOnScriptClose(_render_jpg)
    nuke.addOnScriptClose(_create_csheet)
    nuke.addOnScriptClose(_send_to_render_dir)
    nuke.addAutolabel(ui.custom_autolabel)
    _dropframe()
    _cgtwn()


def abort_modified(func):
    """(Decorator)Abort function when project has been modified."""

    def _func():
        if nuke.modified():
            return False
        func()
    return _func


def _cgtwn():
    cgtwn.CGTeamWork.update_status()

    @abort_modified
    @cgtwn.check_login
    def _nk_file():
        cgtwn.Shot().upload_nk_file()

    @abort_modified
    @cgtwn.check_login
    def _on_close():
        task = nuke.ProgressTask('CGTW')
        task.setMessage('上传单帧')
        cgtwn.Shot().upload_image()
        task.setProgress(50)
        task.setMessage('上传nk文件')
        _nk_file()

    nuke.addOnScriptClose(_on_close)
    nuke.addOnScriptSave(_nk_file)


@abort_modified
def _create_csheet():
    if nuke.numvalue('preferences.wlf_create_csheet', 0.0):
        if nuke.value('root.name'):
            csheet.ContactSheetThread(new_process=True).run()


def _check_project():
    project_directory = nuke.Root()['project_directory'].value()
    if not project_directory:
        nuke.message('工程目录未设置')
    # avoid ValueError of script_directory() when no root.name.
    elif project_directory == '[python {nuke.script_directory()}]':
        nuke.knob('root.project_directory',
                  r"[python {os.path.abspath(os.path.join("
                  r"'D:/temp', nuke.value('root.name', ''), '../'"
                  r")).replace('\\', '/')}]")


def _check_fps():
    default_fps = 30
    fps = nuke.numvalue('root.fps')
    if fps != default_fps:
        nuke.message('当前fps: {}, 默认值: {}'.format(fps, default_fps))


def _lock_connections():
    if nuke.numvalue('preferences.wlf_lock_connections', 0.0):
        nuke.Root()['lock_connections'].setValue(1)
        nuke.Root().setModified(False)


def _jump_frame():
    if nuke.numvalue('preferences.wlf_jump_frame', 0.0) and nuke.exists('_Write.knob.frame'):
        nuke.frame(nuke.numvalue('_Write.knob.frame'))
        nuke.Root().setModified(False)


@abort_modified
def _send_to_render_dir():
    if nuke.numvalue('preferences.wlf_send_to_dir', 0.0):
        asset.sent_to_dir(nuke.value('preferences.wlf_render_dir'))


@abort_modified
def _render_jpg():
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
    """Create this read node's output dir if need."""

    target_dir = os.path.dirname(nuke.filename(nuke.thisNode()))
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)


def add_dropdata_callback():
    """Add callback for datadrop enhance."""

    def _db(type_, data):
        if type_ == 'text/plain' and os.path.basename(data).lower() == 'thumbs.db':
            return True

    def _fbx(type_, data):
        if type_ == 'text/plain' and data.endswith('.fbx'):
            camera_node = nuke.createNode(
                'Camera2',
                'read_from_file True '
                'file {data} '
                'frame_rate 25 '
                'suppress_dialog True '
                'label {{'
                '导入的摄像机：\n'
                '[basename [value file]]\n'
                '注意选择file -> node name}}'.format(data=data))
            camera_node.setName('Camera_3DEnv_1')
            return True

    def _vf(type_, data):
        if type_ == 'text/plain' and data.endswith('.vf'):
            nuke.createNode(
                'Vectorfield',
                'vfield_file "{data}" '
                'file_type vf '
                'label {{[value this.vfield_file]}}'.format(data=data))
            return True

    def _else(type_, data):
        if type_ == 'text/plain':
            nuke.createNode('Read', 'file "{}"'.format(data))
            return True

    def _cgtwn(type_, data):
        if type_ == 'text/plain' and data.startswith('file:///Y:'):
            data = data[8:]
            nuke.createNode('Read', 'file "{}"'.format(data))
            return True

    def _dir(type_, data):
        def _file(type_, data):
            _db(type_, data)
            _fbx(type_, data)
            _vf(type_, data)
            _else(type_, data)

        def _path(type_, data):
            if os.path.isdir(data):
                _dir(type_, data)
            else:
                _file(type_, data)

            return True

        if type_ == 'text/plain' and os.path.isdir(data):
            _dirname = data.replace('\\', '/')
            for i in nuke.getFileNameList(_dirname):
                _path(type_, '/'.join([_dirname, i]))
            return True

    nukescripts.addDropDataCallback(_fbx)
    nukescripts.addDropDataCallback(_vf)
    nukescripts.addDropDataCallback(_db)
    nukescripts.addDropDataCallback(_cgtwn)
    nukescripts.addDropDataCallback(_dir)

    def _catch_all(type_, data):
        print(type_)
        print(data)
        return None

    # nukescripts.addDropDataCallback(_catch_all)
    # nuke.addOnScriptLoad(SNJYW.setProjectRoot)
    # nuke.addOnScriptLoad(SNJYW.setRootFormat)
