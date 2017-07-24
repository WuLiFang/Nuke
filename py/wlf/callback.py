# -*- coding: UTF-8 -*-
"""Add callback for wlf plugins."""

import os

import nuke
import nukescripts

from . import asset, csheet, edit, ui, cgtwn

__version__ = '0.3.5'


def init():
    """Add callback for nuke init phase."""

    nuke.addBeforeRender(create_out_dirs, nodeClass='Write')


def menu():
    """Add callback for nuke menu phase."""

    nukescripts.addDropDataCallback(asset.dropdata_handler)

    nuke.addAutolabel(ui.custom_autolabel)

    nuke.addUpdateUI(_gizmo_to_group_update_ui)

    nuke.addOnCreate(lambda: edit.set_random_glcolor(nuke.thisNode()))
    # nuke.addOnCreate(lambda: asset.DropFrameCheck(
    #     nuke.thisNode()).start(), nodeClass='Read')

    nuke.addOnUserCreate(_gizmo_to_group_on_create)

    nuke.addOnScriptSave(_autoplace)
    nuke.addOnScriptSave(edit.enable_rsmb, kwargs={'prefix': '_'})
    nuke.addOnScriptSave(_check_project)
    nuke.addOnScriptSave(_check_fps)
    nuke.addOnScriptSave(_lock_connections)
    nuke.addOnScriptSave(_jump_frame)
    nuke.addOnScriptSave(cgtwn.on_save_callback)
    nuke.addOnScriptSave(asset.DropFrameCheck.show_dialog)

    nuke.addOnScriptClose(_send_to_render_dir)
    nuke.addOnScriptClose(_render_jpg)
    nuke.addOnScriptClose(cgtwn.on_close_callback)
    nuke.addOnScriptClose(_create_csheet)


def abort_modified(func):
    """(Decorator)Abort function when project has been modified."""

    def _func():
        if nuke.modified():
            return False
        func()
    return _func


@abort_modified
def _create_csheet():
    if nuke.numvalue('preferences.wlf_create_csheet', 0.0):
        if nuke.value('root.name'):
            csheet.ContactSheetThread().run()


def _check_project():
    project_directory = nuke.value('root.project_directory')
    if not project_directory:
        _name = nuke.value('root.name', '')
        if _name:
            _dir = os.path.dirname(_name)
            nuke.knob('root.project_directory', _dir)
            nuke.message('工程目录未设置, 已自动设为: {}'.format(_dir))
        else:
            nuke.message('工程目录未设置')
    # avoid ValueError of script_directory() when no root.name.
    elif project_directory == r"[python {os.path.abspath(os.path.join("\
        r"'D:/temp', nuke.value('root.name', ''), '../'"\
            r")).replace('\\', '/')}]":
        nuke.knob('root.project_directory',
                  r"[python {os.path.join("
                  r"nuke.value('root.name', ''), '../'"
                  r").replace('\\', '/')}]")


def _check_fps():
    default_fps = 30
    if os.path.basename(nuke.value('root.name')).startswith('SNJYW'):
        default_fps = 25
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
        asset.sent_to_dir(
            unicode(nuke.value('preferences.wlf_render_dir'), 'UTF-8'))


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
    if nuke.numvalue('preferences.wlf_autoplace', 0.0) and nuke.modified():
        map(nuke.autoplace, nuke.allNodes())


def _print_name():
    print(nuke.thisNode().name())


def create_out_dirs():
    """Create this read node's output dir if need."""

    target_dir = os.path.dirname(nuke.filename(nuke.thisNode()))
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
