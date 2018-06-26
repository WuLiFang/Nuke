# -*- coding: UTF-8 -*-
"""Setup UI."""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import webbrowser

import cgtwq_uploader
import nuke
import nukescripts  # pylint: disable=import-error
from autolabel import autolabel

import asset
import callback
import cgtwn
import comp
import comp.panels
import edit
import edit_panels
import enable_later
import orgnize
import panels
import scanner
import splitexr
from nuketools import utf8
from wlf.codectools import get_unicode as u

WINDOW_CONTEXT = 0
APPLICATION_CONTEXT = 1
DAG_CONTEXT = 2

LOGGER = logging.getLogger('com.wlf.ui')

RESOURCE_DIR = os.path.abspath(os.path.join(__file__, '../../'))


def add_menu():
    """Add menu for commands and nodes."""

    LOGGER.info('添加菜单')

    def _(*args, **kwargs):
        args = (i.encode('utf-8') if isinstance(i, unicode) else i
                for i in args)
        kwargs = tuple({k: v.encode('utf-8') if isinstance(v, unicode) else v
                        for k, v in kwargs.items()}.items())
        return (args, kwargs)

    def _autocomp():
        try:
            comp.Comp().create_nodes()
        except comp.FootageError:
            nuke.message(utf8('请先导入素材'))

    def _open_help():
        help_page = os.path.join(
            RESOURCE_DIR, 'Documentation/build/html/index.html')
        webbrowser.open(help_page)

    cgtw_menu = _('CGTeamWork', icon='cgteamwork.png')
    all_menu = [
        {_('编辑'): [
            _('同时编辑多个节点', lambda: edit_panels.MultiEdit().show(), 'F2'),
            _('分离图层', lambda: edit.split_layers(nuke.selectedNode()),
              'F3', icon="SplitLayers.png"),
            _("分离rgba",
              lambda: edit.shuffle_rgba(nuke.selectedNode()), 'SHIFT+F3'),
            _("重命名PuzzleMatte",
              lambda: edit_panels.ChannelsRename(prefix='PuzzleMatte').show(), 'F4'),
            _("标记为稍后启用",
              lambda: enable_later.mark_enable(nuke.selectedNodes()), 'SHIFT+D'),
            _('输出当前帧png',
              lambda: comp.render_png(nuke.selectedNodes(), show=True),
              'SHIFT+F7'),
            _("设置帧范围",
              edit.dialog_set_framerange),
            _('转换为相对路径',
              lambda: edit.use_relative_path(nuke.selectedNodes()), icon="utilitiesfolder.png"),
            None,
            _("禁用所有稍后启用节点",
              lambda: enable_later.marked_nodes().disable(), 'CTRL+SHIFT+D'),
            _("修正读取错误", asset.fix_error_read, 'F6'),
            _("Reload所有", edit.reload_all_read_node),
            _("检查缺帧", lambda: asset.warn_missing_frames(show_ok=True)),
            _("检查素材更新", lambda: asset.warn_mtime(
                show_ok=True, show_dialog=True)),
            _("转换单帧为序列",
              edit.replace_sequence),
            {_('整理'): [
                _("整理所选节点(竖式摆放)",
                  lambda: orgnize.autoplace(nuke.selectedNodes()),
                  "L", shortcutContext=DAG_CONTEXT),
                _("清理无用节点",
                  lambda: edit.delete_unused_nodes(message=True)),
                _("所有Gizmo转Group",
                  edit.all_gizmo_to_group),
                _("根据背板重命名所有节点",
                  orgnize.rename_all_nodes),
                _("节点添加Dots变成90度",
                  lambda: orgnize.nodes_add_dots(nuke.selectedNodes())),
                _("所有节点添加Dots变成90度", lambda: orgnize.nodes_add_dots(nuke.allNodes()))
            ]
            }
        ]},
        {_('合成'): [
            _('自动合成', _autocomp, icon='autocomp.png'),
            _('自动合成设置',
              lambda: comp.panels.CompConfigPanel().showModalDialog(), icon='autocomp.png'),
            _('redshift预合成',
              lambda: comp.Precomp.redshift(nuke.selectedNodes()),
              'F1',
              shortcutContext=DAG_CONTEXT,
              icon='autocomp.png')
        ]},
        {cgtw_menu: [
            _('登录', cgtwn.dialog_login),
            _('创建项目文件夹', cgtwn.dialog_create_dirs)
        ]},
        {_('工具'): [
            _('批量自动合成', lambda: comp.panels.BatchCompPanel().showModalDialog(),
              icon='autocomp.png'),
            _('上传mov', lambda: nukescripts.panels.restorePanel(
                'com.wlf.uploader')),
            _('扫描空文件夹', scanner.call_from_nuke),
            _('分离exr', splitexr.Dialog.show),
            _("分割当前文件(根据背板)", orgnize.split_by_backdrop)
        ]},
        {_('帮助'): [
            _('吾立方插件 文档', _open_help),
            _("吾立方网站", lambda: webbrowser.open('http://www.wlf-studio.com/'))
        ]}
    ]

    # Add all menu.
    def _add_menu(menu, parent=nuke.menu("Nuke")):
        assert isinstance(menu, dict)

        for k, v in menu.items():
            m = parent.addMenu(*k[0], **dict(k[1]))
            for i in v:
                if i is None:
                    m.addSeparator()
                elif isinstance(i, dict):
                    _add_menu(i, m)
                elif isinstance(i, tuple):
                    m.addCommand(*i[0], **dict(i[1]))

    for menu in all_menu:
        _add_menu(menu)

    # Set old autoplace shortcut.
    try:
        nuke.menu("Nuke").findItem('Edit').findItem(
            'Node').findItem('Autoplace').setShortcut("Ctrl+L")
    except AttributeError as ex:
        print(ex)

    # create_node_menu
    _plugin_path = '../../plugins'

    m = nuke.menu("Nodes")
    m = m.addMenu('吾立方'.encode('utf-8'), icon='Modify.png')
    create_menu_by_dir(m, os.path.abspath(
        os.path.join(__file__, _plugin_path)))

    # Enhance 'ToolSets' menu.
    def _create_shared_toolsets():
        if not nuke.selectedNodes():
            nuke.message(utf8('未选中任何节点,不能创建工具集'))
            return
        filename = nuke.getInput('ToolSet name')
        if filename:
            nuke.createToolset(filename=os.path.join(
                'Shared', filename), rootPath=RESOURCE_DIR)
        _refresh_toolsets_menu()

    def _refresh_toolsets_menu():
        """Extended nuke function.  """

        nukescripts.toolsets._refreshToolsetsMenu()  # pylint: disable=protected-access
        m = nuke.menu('Nodes').addMenu('ToolSets')
        m.addCommand('刷新'.encode('utf-8'), _refresh_toolsets_menu)
        m.addCommand(
            '创建共享工具集'.encode('utf-8'), _create_shared_toolsets)
        m.addCommand(
            '打开共享工具集文件夹'.encode('utf-8'),
            lambda: webbrowser.open(os.path.join(RESOURCE_DIR, 'ToolSets/Shared')))

    if not getattr(nukescripts.toolsets, '_refreshToolsetsMenu', None):
        setattr(nukescripts.toolsets, '_refreshToolsetsMenu',
                nukescripts.toolsets.refreshToolsetsMenu)
    _refresh_toolsets_menu()
    nukescripts.toolsets.refreshToolsetsMenu = _refresh_toolsets_menu


def add_panel():
    """Add custom pannel. """

    LOGGER.info('添加面板')
    panels.register(cgtwq_uploader.Dialog, '上传mov', 'com.wlf.uploader')


def add_autolabel():
    """Add custom autolabel. """

    LOGGER.info('增强节点标签')
    nuke.addAutolabel(custom_autolabel)


def create_menu_by_dir(parent, dir_):
    """Create menus by given folder structrue."""

    if not os.path.isdir(dir_):
        return False
    _dir = os.path.abspath(dir_)

    def _order(name):
        return ('_0_' if os.path.isdir(os.path.join(_dir, name)) else '_1_') + name

    _listdir = sorted(os.listdir(_dir), key=_order)
    for i in _listdir:
        if i in ['icons', 'Obsolete']:
            continue
        _abspath = os.path.join(_dir, i)
        if os.path.isdir(_abspath):
            m = nuke.menu('Nodes').findItem(
                i) or parent.addMenu(i, icon='{}.png'.format(i))
            create_menu_by_dir(m, _abspath)
        else:
            _name, _ext = os.path.splitext(i)
            if _ext.lower() == '.gizmo':
                parent.addCommand(
                    _name,
                    lambda name=_name: nuke.createNode(name),
                    icon='{}.png'.format(_name))


def custom_autolabel():
    '''
    add addition information on Node in Gui
    '''

    def _add_to_autolabel(text, center=False):

        if not isinstance(text, (str, unicode)):
            return
        ret = u(autolabel()).split('\n')
        ret.insert(1, text)
        ret = '\n'.join(ret).rstrip('\n')
        if center:
            ret = '<div align="center" style="margin:0px;padding:0px">{}</div>'.format(
                ret)
        return ret

    def _keyer():
        label = '输入通道 : ' + u(nuke.value('this.input'))
        ret = _add_to_autolabel(label)
        return ret

    def _read():
        missing_frames = asset.Asset(this).missing_frames(this)
        label = '<style>* {font-family:微软雅黑} span {color:red} b {color:#548DD4}</style>'
        label += '<b>帧范围: </b><span>{} - {}</span>'.format(
            this.firstFrame(), this.lastFrame())
        if missing_frames:
            label += '\n<span>缺帧: {}</span>'.format(missing_frames)
        label += '\n<b>修改日期: </b>{}'.format(this.metadata('input/mtime'))
        ret = _add_to_autolabel(label, True)
        return ret

    def _shuffle():
        channels = dict.fromkeys(['in', 'in2', 'out', 'out2'], '')
        for i in channels.keys():
            channel_value = u(nuke.value('this.' + i))
            if channel_value != 'none':
                channels[i] = channel_value + ' '
        label = (channels['in'] + channels['in2'] + '-> ' +
                 channels['out'] + channels['out2']).rstrip(' ')
        ret = _add_to_autolabel(label)
        return ret

    def _timeoffset():
        return _add_to_autolabel('{:.0f}'.format(this['time_offset'].value()))

    this = nuke.thisNode()
    class_ = this.Class()
    dict_ = {'Keyer': _keyer,
             'Read': _read,
             'Shuffle': _shuffle,
             'TimeOffset': _timeoffset}

    if class_ in dict_:
        ret = dict_[class_]()
        if isinstance(ret, unicode):
            ret = utf8(ret)
        return ret


def panel_show(keyword):
    """Show control panel for matched nodes."""

    nodes = sorted((n for n in nuke.allNodes()
                    if keyword in n.name() and not nuke.numvalue('{}.disable'.format(n.name()), 0)),
                   key=lambda n: n.name(),
                   reverse=True)
    for n in nodes:
        n.showControlPanel()


def setup():
    """Setup ui.   """

    add_autolabel()
    add_menu()
    add_panel()
    callback.CALLBACKS_ON_CREATE.append(
        lambda: edit.set_random_glcolor(nuke.thisNode()))
