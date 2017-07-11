# -*- coding: UTF-8 -*-
"""Setup UI."""

import os

import nuke
from autolabel import autolabel


def add_menu():
    """Add menu for commands and nodes."""

    def _edit(menu):
        m = menu.addMenu("编辑")

        m.addCommand('创建背板', 'wlf.backdrop.create_backdrop()',
                     'ctrl+alt+b', icon="backdrops.png")
        m.addSeparator()
        m.addCommand('选中节点:使用相对路径', 'wlf.edit.nodes_to_relpath(nuke.selectedNodes())',
                     'F2', icon="utilitiesfolder.png")
        m.addCommand(
            "选中节点:分离rgba", "wlf.edit.shuffle_rgba(nuke.selectedNode())")
        m.addCommand('选中节点:分离所有通道', 'wlf.edit.split_layers(nuke.selectedNode())',
                     'F3', icon="SplitLayers.png")
        m.addCommand("选中节点:重命名PuzzleMatte",
                     "wlf.edit.channels_rename(prefix='PuzzleMatte')", "F4")
        m.addCommand("选中节点:添加Dots变成90度",
                     "wlf.edit.nodes_add_dots(nuke.selectedNodes())")
        m.addSeparator()
        m.addCommand("所有读取节点:修正错误", "wlf.edit.fix_error_read()", 'F6')
        m.addCommand("所有读取节点:显示所有缺帧",
                     "wlf.asset.DropFrameCheck.show_dialog(True)")
        m.addCommand("所有读取节点:序列替单帧", "wlf.edit.replace_sequence()")
        m.addSeparator()
        m.addCommand("所有节点:删除未使用的节点",
                     "wlf.edit.delete_unused_nodes(message=True)")
        m.addCommand("所有节点:根据背板重命名", "wlf.edit.rename_all_nodes()")
        m.addCommand("所有节点:根据背板分割文件", "wlf.edit.splitByBackdrop()")
        m.addCommand("所有节点:添加Dots变成90度",
                     "wlf.edit.nodes_add_dots(nuke.allNodes())")
        m.addCommand("所有节点:Gizmo转Group", "wlf.edit.all_gizmo_to_group()")

    def _comp(menu):
        m = menu.addMenu('合成')
        m.addCommand('吾立方自动合成', "wlf.Comp()", icon='autocomp.png')
        m.addCommand('吾立方批量合成', "wlf.Comp.show_dialog()",
                     icon='autocomp.png')
        m.addCommand('arnold预合成', "wlf.precomp.arnold()",
                     icon='autocomp.png')
        _path = os.path.abspath(os.path.join(__file__, '../scenetools.exe'))
        if os.path.isfile(_path):
            _cmd = 'nukescripts.start(r"file://{}")'.format(_path)
        else:
            nuke.tprint('wlf.scenetools: use uncomplied version')
            _cmd = 'import wlf.scenetools;wlf.scenetools.call_from_nuke()'
        m.addCommand('色板\\/成果上传', _cmd)

    def _cgtw(menu):

        m = menu.addMenu('CGTeamWork', icon='cgteamwork.png')
        # m.addCommand('设置工程', "wlf.cgtwn.CGTeamWork.ask_database()")
        m.addCommand('添加note', "wlf.cgtwn.Shot().ask_add_note()")
        # m.addCommand('上传nk文件', "wlf.cgtwn.Shot().upload_nk_file()")
        # m.addCommand('上传单帧', "wlf.cgtwn.Shot().upload_image()")
        m.addCommand('提交检查', "wlf.cgtwn.Shot().sumbit_all()")
        m.addCommand(
            "批量下载",
            'nukescripts.start("file://SERVER/scripts/NukePlugins/CGTeamWork工具/CGTW批量下载.bat")')

    def _create_node_menu():
        _plugin_path = '../../../plugins'

        m = nuke.menu("Nodes")
        m = m.addMenu('吾立方', icon='Modify.png')
        nuke.tprint(os.path.abspath(os.path.join(__file__, _plugin_path)))
        create_menu_by_dir(m, os.path.abspath(
            os.path.join(__file__, _plugin_path)))
        m.addCommand(
            "吾立方网站", "nukescripts.start('http://www.wlf-studio.com/')")

    _menubar = nuke.menu("Nuke")

    _edit(_menubar)
    _comp(_menubar)
    _cgtw(_menubar)
    _create_node_menu()


def create_menu_by_dir(parent, dir_):
    """Create menus by given folder structrue."""

    if not os.path.isdir(dir_):
        return False
    _dir = os.path.abspath(dir_)

    def _order(name):
        return ('_0_' if os.path.isdir(os.path.join(_dir, name)) else '_1_') + name

    _listdir = os.listdir(_dir)
    _listdir.sort(key=_order)
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
    _class = nuke.thisNode().Class()

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
        dropframes = nuke.value('this.dropframes', '')
        if dropframes:
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
    list_ = []
    for n in nuke.allNodes():
        name = n.name()
        if keyword in name and nuke.numvalue('{}.disable'.format(name), 0):
            list_.append(n)
    list_.sort(key=_node_name, reverse=True)
    for n in list_:
        n.showControlPanel()
