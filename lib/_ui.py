# -*- coding: UTF-8 -*-
"""Setup UI."""

import os

import nuke
import nukescripts
from autolabel import autolabel

import wlf

import asset
import precomp
import edit
import cgtwn
import orgnize
import comp
import uploader
import splitexr
import scanner
import panels

__version__ = '0.5.2'

WINDOW_CONTEXT = 0
APPLICATION_CONTEXT = 1
DAG_CONTEXT = 2


def add_menu():
    """Add menu for commands and nodes."""

    def _edit(menu):
        m = menu.addMenu("编辑")

        m.addCommand("分离rgba",
                     lambda: edit.shuffle_rgba(nuke.selectedNode()))
        m.addCommand('分离所有通道', lambda: edit.split_layers(nuke.selectedNode()),
                     'F3', icon="SplitLayers.png")
        m.addCommand("重命名PuzzleMatte",
                     lambda: edit.channels_rename(prefix='PuzzleMatte'), 'F4')
        m.addCommand("标记为_enable_",
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

        m.addCommand("禁用所有_enable_节点",
                     lambda: edit.disable_nodes(prefix='_enable_'), 'CTRL+SHIFT+D')
        m.addCommand(
            "修正读取错误", edit.fix_error_read, 'F6')
        m.addCommand(
            "Reload所有", edit.reload_all_read_node)
        m.addCommand("检查缺帧", asset.DropFrames.check)
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
            '创建项目色板', cgtwn.dialog_create_csheet)
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

    def _create_node_menu():
        _plugin_path = '../../plugins'

        m = nuke.menu("Nodes")
        m = m.addMenu('吾立方', icon='Modify.png')
        nuke.tprint(os.path.abspath(os.path.join(__file__, _plugin_path)))
        create_menu_by_dir(m, os.path.abspath(
            os.path.join(__file__, _plugin_path)))
        m.addCommand(
            "吾立方网站", "nukescripts.start('http://www.wlf-studio.com/')")

    menubar = nuke.menu("Nuke")

    _edit(menubar)
    _comp(menubar)
    _tools(menubar)
    if wlf.cgtwq.MODULE_ENABLE:
        _cgtw(menubar)
    _create_node_menu()


def add_panel():
    """Add custom pannel. """
    panels.register(uploader.Dialog, '上传mov', 'com.wlf.uploader')


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


def custom_autolabel(enable_text_style=True):
    '''
    add addition information on Node in Gui
    '''
    this = nuke.thisNode()
    _class = this.Class()

    def _add_to_autolabel(label):
        if not isinstance(label, str):
            return
        _ret = autolabel().split('\n')
        _ret.insert(1, label)
        _ret = '\n'.join(_ret).rstrip('\n')
        return _ret

    if _class == 'Keyer':
        label = '输入通道 : ' + nuke.value('this.input')
    elif _class == 'Read':
        dropframes = str(asset.DropFrames.get(nuke.filename(this), ''))
        if dropframes:
            nuke.warning('{}:[dropframes]{}'.format(this.name(), dropframes))
            if enable_text_style:
                dropframes = '\n<span style=\"color:red\">缺帧:{}</span>'.format(
                    dropframes)
            else:
                dropframes = '\n缺帧:' + dropframes
        if enable_text_style:
            label = '<span style=\"color:#548DD4;font-family:微软雅黑\">'\
                '<b> 帧范围 :</b></span> '\
                '<span style=\"color:red\">{} - {}</span>{}'
            label = label.format(nuke.value('this.first'),
                                 nuke.value('this.last'), dropframes)
        else:
            label = '帧范围 :' + nuke.value('this.first') + \
                ' - ' + nuke.value('this.last')
    elif _class == 'Shuffle':
        channels = dict.fromkeys(['in', 'in2', 'out', 'out2'], '')
        for i in channels.keys():
            channel_value = nuke.value('this.' + i)
            if channel_value != 'none':
                channels[i] = channel_value + ' '
        label = (channels['in'] + channels['in2'] + '-> ' +
                 channels['out'] + channels['out2']).rstrip(' ')
    else:
        return

    return _add_to_autolabel(label)


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
