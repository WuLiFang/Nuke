# -*- coding: UTF-8 -*-
"""Setup UI."""

import os
import logging
import webbrowser

import nuke
import nukescripts
from autolabel import autolabel

import wlf
import wlf.uploader

import asset
import precomp
import edit
import edit_panels
import cgtwn
import orgnize
import comp
import splitexr
import scanner
import panels

__version__ = '0.5.4'

WINDOW_CONTEXT = 0
APPLICATION_CONTEXT = 1
DAG_CONTEXT = 2

LOGGER = logging.getLogger('com.wlf.ui')

RESOURCE_DIR = os.path.abspath(os.path.join(__file__, '../../'))


def add_menu():
    """Add menu for commands and nodes."""

    LOGGER.info(u'添加菜单')

    def _edit(menu):
        m = menu.addMenu("编辑")

        m.addCommand('同时编辑多个节点', lambda: edit_panels.MultiEdit().show(), 'F2')
        m.addCommand('分离图层', lambda: edit.split_layers(nuke.selectedNode()),
                     'F3', icon="SplitLayers.png")
        m.addCommand("分离rgba",
                     lambda: edit.shuffle_rgba(nuke.selectedNode()), 'SHIFT+F3')
        m.addCommand("重命名PuzzleMatte",
                     lambda: edit_panels.ChannelsRename(prefix='PuzzleMatte').show(), 'F4')
        m.addCommand("标记为稍后启用",
                     lambda: edit.mark_enable(nuke.selectedNodes()), 'SHIFT+D')
        m.addCommand('输出当前帧png',
                     lambda: comp.render_png(nuke.selectedNodes(), show=True),
                     'SHIFT+F7')
        m.addCommand("设置帧范围",
                     edit.dialog_set_framerange)
        m.addCommand('转换为相对路径',
                     lambda: edit.nodes_to_relpath(nuke.selectedNodes()),
                     icon="utilitiesfolder.png")

        m.addSeparator()

        m.addCommand("禁用所有稍后启用节点",
                     lambda: edit.marked_nodes().disable(), 'CTRL+SHIFT+D')
        m.addCommand(
            "修正读取错误", asset.fix_error_read, 'F6')
        m.addCommand(
            "Reload所有", edit.reload_all_read_node)
        m.addCommand("检查缺帧", lambda: asset.DropFrames.check(show_ok=True))
        m.addCommand("检查素材更新", lambda: asset.warn_mtime(
            show_ok=True, show_dialog=True))
        m.addCommand("转换单帧为序列",
                     edit.replace_sequence)

        n = m.addMenu('整理')
        n.addCommand("整理所选节点(竖式摆放)",
                     lambda: orgnize.autoplace(nuke.selectedNodes()),
                     "L", shortcutContext=DAG_CONTEXT)
        try:
            nuke.menu("Nuke").findItem('Edit').findItem(
                'Node').findItem('Autoplace').setShortcut("Ctrl+L")
        except AttributeError as ex:
            print(ex)
        n.addCommand("清理无用节点",
                     lambda: edit.delete_unused_nodes(message=True))
        n.addCommand("所有Gizmo转Group",
                     edit.all_gizmo_to_group)
        n.addCommand("根据背板重命名所有节点",
                     edit.rename_all_nodes)
        n.addCommand("节点添加Dots变成90度",
                     lambda: edit.nodes_add_dots(nuke.selectedNodes()))
        n.addCommand("所有节点添加Dots变成90度",
                     lambda: edit.nodes_add_dots(nuke.allNodes()))

    def _comp(menu):
        m = menu.addMenu('合成')

        def _autocomp():
            try:
                comp.Comp()
            except comp.FootageError:
                nuke.message('请先导入素材')
        m.addCommand('自动合成', _autocomp, icon='autocomp.png')
        m.addCommand('redshift预合成',
                     lambda: precomp.Precomp(
                         nuke.selectedNodes(), renderer='redshift'),
                     'F1',
                     shortcutContext=DAG_CONTEXT,
                     icon='autocomp.png')
        _path = os.path.abspath(os.path.join(
            __file__, '../../scenetools/scenetools.exe'))

    def _cgtw(menu):

        m = menu.addMenu('CGTeamWork', icon='cgteamwork.png')
        m.addCommand(
            '登录', cgtwn.dialog_login)
        m.addCommand(
            '添加note', lambda: cgtwn.CurrentShot().ask_add_note())
        m.addCommand(
            '提交单帧', lambda: cgtwn.CurrentShot().submit_image())
        m.addCommand(
            '提交视频', lambda: cgtwn.CurrentShot().submit_video())
        m.addCommand(
            "批量下载", r"nuke.message('已在<b>CGTeamWork右键菜单</b>中集成此功能\n<i>预定删除此菜单</i>')")
        m.addCommand(
            '创建项目色板', lambda: cgtwn.ContactSheetPanel().show())
        m.addCommand(
            '创建项目文件夹', cgtwn.dialog_create_dirs)

    def _tools(menu):
        m = menu.addMenu('工具')
        m.addCommand('批量自动合成', comp.Comp.show_dialog,
                     icon='autocomp.png')
        m.addCommand(
            '创建色板', wlf.csheet.dialog_create_html)
        m.addCommand('上传mov', lambda: nukescripts.panels.restorePanel(
            'com.wlf.uploader'))
        m.addCommand('扫描空文件夹', scanner.call_from_nuke)
        m.addCommand('分离exr', splitexr.Dialog.show)
        m.addCommand("分割当前文件(根据背板)",
                     edit.split_by_backdrop)

    def _help(menu):
        def _open_help():
            help_page = os.path.join(
                RESOURCE_DIR, 'Documentation/build/html/index.html')
            webbrowser.open(help_page)
        m = menu.addMenu('帮助')

        m.addCommand('吾立方插件 文档', _open_help)
        m.addCommand(
            "吾立方网站", lambda: webbrowser.open('http://www.wlf-studio.com/'))

    def _create_node_menu():
        _plugin_path = '../../plugins'

        m = nuke.menu("Nodes")
        m = m.addMenu('吾立方', icon='Modify.png')
        create_menu_by_dir(m, os.path.abspath(
            os.path.join(__file__, _plugin_path)))

    def _create_shared_toolsets():
        if not nuke.selectedNodes():
            nuke.message('未选中任何节点,不能创建工具集')
            return
        filename = nuke.getInput('ToolSet name')
        if filename:
            nuke.createToolset(filename=os.path.join(
                'Shared', filename), rootPath=RESOURCE_DIR)
        _refresh_toolsets_menu()

    def _toolsets():
        m = nuke.menu('Nodes').addMenu('ToolSets')
        m.addCommand('刷新', _refresh_toolsets_menu)
        m.addCommand(
            '创建共享工具集', _create_shared_toolsets)
        m.addCommand(
            '打开共享工具集文件夹', lambda: webbrowser.open(os.path.join(RESOURCE_DIR, 'ToolSets/Shared')))

    _raw_refresh_toolsets_menu = nukescripts.toolsets.refreshToolsetsMenu

    def _refresh_toolsets_menu():
        """Extend nuke function.  """

        _raw_refresh_toolsets_menu()
        _toolsets()

    nukescripts.toolsets.refreshToolsetsMenu = _refresh_toolsets_menu

    menubar = nuke.menu("Nuke")

    _edit(menubar)
    _comp(menubar)
    _tools(menubar)
    if wlf.cgtwq.MODULE_ENABLE:
        _cgtw(menubar)
    _help(menubar)
    _create_node_menu()
    _toolsets()


def add_panel():
    """Add custom pannel. """
    LOGGER.info(u'添加面板')
    panels.register(wlf.uploader.Dialog, '上传mov', 'com.wlf.uploader')


def add_autolabel():
    """Add custom autolabel. """
    LOGGER.info(u'增强节点标签')
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
                parent.addCommand(_name, 'nuke.createNode("{0}")'.format(
                    _name), icon='{}.png'.format(_name))


def custom_autolabel():
    '''
    add addition information on Node in Gui
    '''
    this = nuke.thisNode()
    _class = this.Class()
    ret = None

    def _add_to_autolabel(text, center=False):
        if not isinstance(text, (str, unicode)):
            return
        ret = autolabel().split('\n')
        ret.insert(1, text)
        ret = '\n'.join(ret).rstrip('\n')
        if center:
            ret = '<div align="center" style="margin:0px;padding:0px">{}</div>'.format(
                ret)
        return ret

    if _class == 'Keyer':
        label = '输入通道 : ' + nuke.value('this.input')
        ret = _add_to_autolabel(label)
    elif _class == 'Read':
        dropframes = str(asset.DropFrames.get(nuke.filename(this), ''))
        label = '<style>* {font-family:微软雅黑} span {color:red} b {color:#548DD4}</style>'
        label += '<b>帧范围: </b><span>{} - {}</span>'.format(
            this.firstFrame(), this.lastFrame())
        if dropframes:
            nuke.warning('{}:[dropframes]{}'.format(this.name(), dropframes))
            label += '\n<span>缺帧: {}</span>'.format(dropframes)
        label += '\n<b>修改日期: </b>{}'.format(this.metadata('input/mtime'))
        ret = _add_to_autolabel(label, True)
    elif _class == 'Shuffle':
        channels = dict.fromkeys(['in', 'in2', 'out', 'out2'], '')
        for i in channels.keys():
            channel_value = nuke.value('this.' + i)
            if channel_value != 'none':
                channels[i] = channel_value + ' '
        label = (channels['in'] + channels['in2'] + '-> ' +
                 channels['out'] + channels['out2']).rstrip(' ')
        ret = _add_to_autolabel(label)

    return ret


def panel_show(keyword):
    """Show control panel for matched nodes."""

    def _node_name(node):
        return node.name()
    nodes = sorted((n for n in nuke.allNodes()
                    if keyword in n.name() and not nuke.numvalue('{}.disable'.format(n.name()), 0)),
                   key=lambda n: n.name(),
                   reverse=True)
    for n in nodes:
        n.showControlPanel()
