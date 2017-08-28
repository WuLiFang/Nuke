# -*- coding: UTF-8 -*-
"""Setup UI."""

import os

import nuke
from autolabel import autolabel

import wlf

import asset
import precomp
import edit
import cgtwn
import orgnize
import comp
import uploader

__version__ = '0.4.0'

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
        m.addSeparator()
        m.addCommand("节点标记为_enable_",
                     lambda: edit.mark_enable(nuke.selectedNodes()), 'SHIFT+D')
        m.addCommand("禁用所有_enable_节点",
                     lambda: edit.disable_nodes(prefix='_enable_'), 'CTRL+SHIFT+D')
        m.addSeparator()
        m.addCommand(
            "修正错误读取节点", edit.fix_error_read, 'F6')
        m.addCommand(
            "Reload所有读取节点", edit.reload_all_read_node)
        m.addCommand("显示所有缺帧",
                     lambda: asset.DropFrameCheck.show_dialog(True))
        m.addCommand("单帧转序列",
                     edit.replace_sequence)
        m.addCommand("设置所选节点帧范围",
                     edit.dialog_set_framerange)
        m.addCommand("清理无用节点",
                     lambda: edit.delete_unused_nodes(message=True))
        m.addCommand('节点转为相对路径',
                     lambda: edit.nodes_to_relpath(nuke.selectedNodes()),
                     icon="utilitiesfolder.png")
        m.addCommand("所有Gizmo转Group",
                     edit.all_gizmo_to_group)
        n = m.addMenu('整理文件')
        n.addCommand("竖式自动摆放节点",
                     lambda: orgnize.autoplace(nuke.selectedNodes()),
                     "L", shortcutContext=DAG_CONTEXT)
        try:
            nuke.menu("Nuke").findItem('Edit').findItem(
                'Node').findItem('Autoplace').setShortcut("Ctrl+L")
        except AttributeError as ex:
            print(ex)
        n.addCommand("根据背板重命名所有节点",
                     edit.rename_all_nodes)
        n.addCommand("根据背板分割为多个文件文件",
                     edit.split_by_backdrop)
        n.addCommand("节点添加Dots变成90度",
                     lambda: edit.nodes_add_dots(nuke.selectedNodes()))
        n.addCommand("所有节点添加Dots变成90度",
                     lambda: edit.nodes_add_dots(nuke.allNodes()))

    def _comp(menu):
        m = menu.addMenu('合成')
        m.addCommand('自动合成', comp.Comp,
                     icon='autocomp.png')
        m.addCommand('批量自动合成', comp.Comp.show_dialog,
                     icon='autocomp.png')
        m.addCommand('输出当前帧png',
                     lambda: comp.render_png(nuke.selectedNodes(), show=True),
                     'SHIFT+F7')
        m.addCommand('redshift预合成',
                     lambda: precomp.Precomp(
                         nuke.selectedNodes(), renderer='redshift'),
                     icon='autocomp.png')
        _path = os.path.abspath(os.path.join(
            __file__, '../../scenetools/scenetools.exe'))
        m.addCommand(
            '创建色板', wlf.csheet.dialog_create_html)
        m.addCommand('上传工具', uploader.call_from_nuke)

    def _cgtw(menu):

        m = menu.addMenu('CGTeamWork', icon='cgteamwork.png')
        m.addCommand(
            '帐号登录', cgtwn.dialog_login)
        m.addCommand(
            '添加note', lambda: cgtwn.CurrentShot().ask_add_note())
        m.addCommand(
            '提交单帧', lambda: cgtwn.CurrentShot().submit_image())
        m.addCommand(
            '提交视频', lambda: cgtwn.CurrentShot().submit_video())
        m.addCommand(
            "批量下载",
            r'import subprocess;'
            r'subprocess.Popen(r"\\SERVER\scripts\cgteamwork\downloader\run.bat")')
        m.addCommand(
            '为项目创建色板', cgtwn.dialog_create_csheet)
        m.addCommand(
            '为项目创建文件夹', cgtwn.dialog_create_dirs)

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
    if wlf.cgtwq.MODULE_ENABLE:
        _cgtw(menubar)
    _create_node_menu()


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
        dropframes = str(asset.DropFrameCheck.dropframes_dict.get(
            nuke.filename(this), ''))
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
