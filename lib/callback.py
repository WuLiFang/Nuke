# -*- coding: UTF-8 -*-
"""Add callback for wlf plugins."""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import sys

import nuke

import asset
import cgtwn
import edit
import orgnize
from node import Last, wlf_write_node
from nuketools import utf8
from wlf import csheet
from wlf.path import get_unicode as u

LOGGER = logging.getLogger('com.wlf.callback')


class Callbacks(list):
    """Failsafe callbacks executor.  """

    def execute(self, *args, **kwargs):
        ret = None
        try:
            for i in self:
                try:
                    ret = i(*args, **kwargs) or ret
                except:
                    import inspect
                    try:
                        lineno = inspect.getsourcelines(i)[1]
                    except IOError:
                        lineno = None
                    LOGGER.error(
                        'Error during execute callback: %s(%s,%s):'
                        '\n%s : %s',
                        i.__name__,
                        args, kwargs,
                        inspect.getsourcefile(i),
                        lineno,
                        exc_info=True)
        except RuntimeError:
            pass
        return ret


CALLBACKS_BEFORE_RENDER = Callbacks()
CALLBACKS_ON_CREATE = Callbacks()
CALLBACKS_ON_DROP_DATA = Callbacks()
CALLBACKS_ON_USER_CREATE = Callbacks()
CALLBACKS_ON_SCRIPT_LOAD = Callbacks()
CALLBACKS_ON_SCRIPT_SAVE = Callbacks()
CALLBACKS_ON_SCRIPT_CLOSE = Callbacks()
CALLBACKS_UPDATE_UI = Callbacks()


def setup():
    """Setup callbacks.  """

    CALLBACKS_BEFORE_RENDER.extend([
        create_out_dirs
    ])
    if nuke.GUI:
        CALLBACKS_ON_CREATE.extend(
            [
                lambda: edit.set_random_glcolor(nuke.thisNode())
            ])
        CALLBACKS_ON_DROP_DATA.extend(
            [
                asset.dropdata_handler
            ])
        CALLBACKS_ON_USER_CREATE.extend(
            [
                _gizmo_to_group_on_create
            ]
        )
        CALLBACKS_ON_SCRIPT_LOAD.extend(
            [
                Last.on_load_callback,
                lambda: asset.warn_mtime(show_dialog=True),
                asset.Localization.update,
                asset.warn_missing_frames,
                _add_root_info,
                _eval_proj_dir
            ])
        CALLBACKS_ON_SCRIPT_SAVE.extend(
            [
                Last.on_save_callback,
                _autoplace,
                _enable_node,
                _lock_connections,
                _jump_frame,
                lambda: asset.warn_mtime(show_dialog=True),
                asset.warn_missing_frames,
                _check_project
            ])
        CALLBACKS_ON_SCRIPT_CLOSE.extend(
            [
                _send_to_render_dir,
                _render_jpg,
                _create_csheet
            ])
        CALLBACKS_UPDATE_UI.extend(
            [
                _gizmo_to_group_update_ui
            ])

    if cgtwn.cgtwq.MODULE_ENABLE:
        LOGGER.info('启用CGTeamWork集成 23')
        CALLBACKS_ON_SCRIPT_LOAD.append(cgtwn.on_load_callback)
        CALLBACKS_ON_SCRIPT_SAVE.append(cgtwn.on_save_callback)
        CALLBACKS_ON_SCRIPT_CLOSE.append(cgtwn.on_close_callback)
    else:
        # Check fps already included in cgtwn
        CALLBACKS_ON_SCRIPT_CLOSE.append(_check_fps)


def install():
    """Install all callbacks to nuke.  """

    if nuke.GUI:
        asset.Localization.start_upate()
    nuke.addBeforeRender(CALLBACKS_BEFORE_RENDER.execute)
    nuke.addOnScriptLoad(CALLBACKS_ON_SCRIPT_LOAD.execute)
    nuke.addOnScriptSave(CALLBACKS_ON_SCRIPT_SAVE.execute)
    nuke.addOnScriptClose(CALLBACKS_ON_SCRIPT_CLOSE.execute)
    nuke.addOnCreate(CALLBACKS_ON_CREATE.execute)
    nuke.addUpdateUI(CALLBACKS_UPDATE_UI.execute)
    if nuke.GUI:
        import nukescripts
        nukescripts.addDropDataCallback(CALLBACKS_ON_DROP_DATA.execute)


def abort_modified(func):
    """(Decorator)Abort function when project has been modified."""

    def _func():
        if nuke.Root().modified():
            return False
        func()
    return _func


def _enable_node():
    if nuke.numvalue('preferences.wlf_enable_node', 0.0):
        LOGGER.debug('Enable "__enable__" nodes.')
        edit.marked_nodes().enable()


@abort_modified
def _create_csheet():
    if nuke.numvalue('preferences.wlf_create_csheet', 0.0):
        if nuke.value('root.name'):
            csheet.create_html_from_dir(os.path.join(
                nuke.value('root.project_directory'), 'images'))


def _eval_proj_dir():
    LOGGER.debug('Eval project dir')
    if nuke.numvalue('preferences.wlf_eval_proj_dir', 0.0):
        attr = 'root.project_directory'
        nuke.knob(attr, os.path.abspath(nuke.value(attr)).replace('\\', '/'))


def _check_project():
    LOGGER.debug('Check project dir')
    project_directory = nuke.value('root.project_directory')
    if not project_directory:
        _name = nuke.value('root.name', '')
        if _name:
            _dir = os.path.dirname(_name)
            nuke.knob('root.project_directory', _dir)
            nuke.message(b'工程目录未设置, 已自动设为: {}'.format(_dir))
        else:
            nuke.message(b'工程目录未设置')
    # avoid ValueError of script_directory() when no root.name.
    elif project_directory == r"[python {os.path.abspath(os.path.join("\
        r"'D:/temp', nuke.value('root.name', ''), '../'"\
            r")).replace('\\', '/')}]":
        nuke.knob('root.project_directory',
                  r"[python {os.path.join("
                  r"nuke.value('root.name', ''), '../'"
                  r").replace('\\', '/')}]")


def _check_fps():
    default_fps = cgtwn.CurrentShot.get_info().get('fps', 30)
    LOGGER.debug('Check fps. default: %s', default_fps)
    fps = nuke.numvalue('root.fps')

    if fps != default_fps:
        confirm = nuke.ask(b'当前fps: {}, 设为默认值: {} ?'.format(fps, default_fps))
        if confirm:
            nuke.knob('root.fps', str(default_fps))


def _lock_connections():
    if nuke.numvalue('preferences.wlf_lock_connections', 0.0):
        LOGGER.debug('Lock connections')
        nuke.Root()['lock_connections'].setValue(1)
        nuke.Root().setModified(False)


def _jump_frame():
    if nuke.numvalue('preferences.wlf_jump_frame', 0.0):
        LOGGER.debug('Jump frame')
        n = wlf_write_node()
        if n:
            nuke.frame(n['frame'].value())
            nuke.Root().setModified(False)


@abort_modified
def _send_to_render_dir():
    if nuke.numvalue('preferences.wlf_send_to_dir', 0.0):
        render_dir = nuke.value('preferences.wlf_render_dir')
        LOGGER.debug('Send to render dir: %s', render_dir)
        asset.sent_to_dir(render_dir)


@abort_modified
def _render_jpg():
    if nuke.numvalue('preferences.wlf_render_jpg', 0.0):
        n = wlf_write_node()
        if n:
            LOGGER.debug('render_jpg: %s', n.name())
            try:
                n['bt_render_JPG'].execute()
            except RuntimeError as ex:
                nuke.message(str(ex))


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
    _has_temp_knob = nuke.exists(
        utf8('{}.{}'.format(u(n.name()), _temp_knob_name)))

    if _has_temp_knob:
        n = edit.gizmo_to_group(n)
        n.removeKnob(n[_temp_knob_name])
        n.removeKnob(n['User'])


def clean():
    """Remove error callback.  """

    groups = ('onScriptLoads', 'onScriptSaves', 'onScriptCloses',
              'onDestroys', 'onCreates', 'onUserCreates', 'knobChangeds',
              'updateUIs', 'renderProgresses',
              'beforeBackgroundRenders', 'afterBackgroundRenders',
              'beforeBackgroundFrameRenders', 'afterBackgroundFrameRenders',
              'beforeRenders', 'afterRenders',
              'beforeFrameRenders', 'afterFrameRenders',
              'validateFilenames')
    for group in groups:
        group = getattr(nuke, group, None)
        if not isinstance(group, dict):
            continue
        for callbacks in group.values():
            for callback in callbacks:
                try:
                    str(callback)
                except ValueError:
                    callbacks.remove(callback)


def _autoplace():
    if nuke.numvalue('preferences.wlf_autoplace', 0.0) and nuke.Root().modified():
        autoplace_type = nuke.numvalue('preferences.wlf_autoplace_type', 0.0)
        LOGGER.debug('Autoplace. type: %s', autoplace_type)
        if autoplace_type == 0.0:
            orgnize.autoplace(async_=False)
        else:
            map(nuke.autoplace, nuke.allNodes())


def _add_root_info():
    """add info to root.  """

    artist = nuke.value('preferences.wlf_artist', '')
    if not artist:
        return
    if not nuke.exists('root.wlf'):
        n = nuke.Root()
        k = nuke.Tab_Knob('wlf', b'吾立方')
        k.setFlag(nuke.STARTLINE)
        n.addKnob(k)

        k = nuke.String_Knob('wlf_artist', b'制作人')
        k.setFlag(nuke.STARTLINE)
        k.setValue(artist)
        n.addKnob(k)
    else:
        if nuke.exists('root.wlf_artist') and not nuke.value('root.wlf_artist', ''):
            nuke.knob('root.wlf_artist', artist)


def create_out_dirs():
    """Create this read node's output dir if need."""

    this = nuke.thisNode()
    if this.Class() != 'Read':
        return
    if this['disable'].value():
        return
    target_dir = os.path.dirname(nuke.filename(this))
    if not os.path.isdir(target_dir):
        LOGGER.debug('Create dir: %s', target_dir)
        os.makedirs(target_dir)
