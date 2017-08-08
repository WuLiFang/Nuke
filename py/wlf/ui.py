# -*- coding: UTF-8 -*-
"""Setup UI."""

import os

import nuke
from autolabel import autolabel

from . import asset, cgtwn

__version__ = '0.2.3'


def add_menu():
    """Add menu for commands and nodes."""

    def _edit(menu):
        m = menu.addMenu("编辑")

        m.addCommand(
            "分离rgba", "import wlf.edit; wlf.edit.shuffle_rgba(nuke.selectedNode())")
        m.addCommand('分离所有通道', 'import wlf.edit; wlf.edit.split_layers(nuke.selectedNode())',
                     'F3', icon="SplitLayers.png")
        m.addCommand("重命名PuzzleMatte",
                     "import wlf.edit; wlf.edit.channels_rename(prefix='PuzzleMatte')", "F4")
        m.addSeparator()
        m.addCommand("节点标记为_enable_",
                     "import wlf.edit; wlf.edit.mark_enable(nuke.selectedNodes())", 'SHIFT+D')
        m.addCommand("禁用所有_enable_节点",
                     "import wlf.edit; wlf.edit.disable_nodes(prefix='_enable_')", "CTRL+SHIFT+D")
        m.addSeparator()
        m.addCommand(
            "修正错误读取节点", "import wlf.edit; wlf.edit.fix_error_read()", 'F6')
        m.addCommand("显示所有缺帧",
                     "import wlf.asset; wlf.asset.DropFrameCheck.show_dialog(True)")
        m.addCommand("单帧转序列",
                     "import wlf.edit; wlf.edit.replace_sequence()")
        m.addCommand("清理无用节点",
                     "import wlf.edit; wlf.edit.delete_unused_nodes(message=True)")
        m.addCommand('节点转为相对路径',
                     'import wlf.edit; wlf.edit.nodes_to_relpath(nuke.selectedNodes())',
                     icon="utilitiesfolder.png")
        m.addCommand("所有Gizmo转Group",
                     "import wlf.edit; wlf.edit.all_gizmo_to_group()")
        n = m.addMenu('整理文件')
        n.addCommand('创建背板', 'import wlf.backdrop; wlf.backdrop.create_backdrop()',
                     'ctrl+alt+b', icon="backdrops.png")
        n.addCommand("根据背板重命名所有节点",
                     "import wlf.edit; wlf.edit.rename_all_nodes()")
        n.addCommand("根据背板分割为多个文件文件",
                     "import wlf.edit; wlf.edit.splitByBackdrop()")
        n.addCommand("节点添加Dots变成90度",
                     "import wlf.edit; wlf.edit.nodes_add_dots(nuke.selectedNodes())")
        n.addCommand("所有节点添加Dots变成90度",
                     "import wlf.edit; wlf.edit.nodes_add_dots(nuke.allNodes())")

    def _comp(menu):
        m = menu.addMenu('合成')
        m.addCommand('自动合成', "import wlf.comp; wlf.comp.Comp()",
                     icon='autocomp.png')
        m.addCommand('批量自动合成', "import wlf.comp; wlf.comp.Comp.show_dialog()",
                     icon='autocomp.png')
        m.addCommand('输出当前帧png',
                     "import wlf.comp; wlf.comp.render_png(nuke.selectedNodes(), show=True)",
                     'SHIFT+F7')
        m.addCommand('redshift预合成',
                     "import wlf.precomp; wlf.precomp.redshift(nuke.selectedNodes())",
                     icon='autocomp.png')
        m.addCommand('arnold预合成', "import wlf.precomp; wlf.precomp.arnold()",
                     icon='autocomp.png')
        _path = os.path.abspath(os.path.join(
            __file__, '../../../scenetools/scenetools.exe'))
        m.addCommand(
            '创建色板', 'import wlf.csheet; wlf.csheet.dialog_create_html()')
        if os.path.isfile(_path):
            _cmd = 'nukescripts.start(r"file://{}")'.format(_path)
        else:
            nuke.pluginAddPath(os.path.abspath(os.path.join(_path, '../')))
            nuke.tprint('wlf.scenetools: use uncomplied version')
            _cmd = 'import scenetools;scenetools.call_from_nuke()'
        m.addCommand('上传工具', _cmd)

    def _cgtw(menu):

        m = menu.addMenu('CGTeamWork', icon='cgteamwork.png')
        # m.addCommand('设置工程', "import wlf.cgtwn; wlf.cgtwn.CGTeamWork.ask_database()")
        m.addCommand(
            '添加note', "import wlf.cgtwn; wlf.cgtwn.Shot().ask_add_note()")
        # m.addCommand('上传nk文件', "import wlf.cgtwn; wlf.cgtwn.Shot().upload_nk_file()")
        # m.addCommand('上传单帧', "import wlf.cgtwn; wlf.cgtwn.Shot().upload_image()")
        m.addCommand(
            '提交单帧', "import wlf.cgtwn; wlf.cgtwn.Shot().submit_image()")
        m.addCommand(
            '提交视频', "import wlf.cgtwn; wlf.cgtwn.Shot().submit_video()")
        m.addCommand(
            "批量下载",
            r'import subprocess; subprocess.Popen(r"\\SERVER\scripts\cgteamwork\downloader\run.bat")')
        # m.addCommand('重新登录', "import wlf.cgtwn; wlf.cgtwn.CGTeamWork.update_status()")

    def _create_node_menu():
        _plugin_path = '../../../plugins'

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
    if cgtwn.MODULE_ENABLE:
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
