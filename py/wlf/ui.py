# -*- coding: UTF-8 -*-
import os

import nuke
from autolabel import autolabel

import callback
import pref


def add_menu():
    
    def _edit(menu):
        m = menu.addMenu("编辑")

        m.addCommand('创建背板', 'wlf.backdrop.create_backdrop()', 'ctrl+alt+b', icon="backdrops.png")
        m.addSeparator()
        m.addCommand('选中节点:使用相对路径', 'wlf.edit.nodes_to_relpath(nuke.selectedNodes())', 'F2', icon="utilitiesfolder.png")
        m.addCommand("选中节点:分离rgba","wlf.edit.shuffle_rgba(nuke.selectedNode())")
        m.addCommand('选中节点:分离所有通道', 'wlf.edit.split_layers(nuke.selectedNode())', 'F3',icon="SplitLayers.png")
        m.addCommand("选中节点:重命名PuzzleMatte","wlf.edit.channels_rename(prefix='PuzzleMatte')","F4")
        m.addCommand("选中节点:添加Dots变成90度","wlf.edit.nodes_add_dots(nuke.selectedNodes())")
        m.addSeparator()
        m.addCommand("所有读取节点:修正错误" , "wlf.edit.fix_error_read()", 'F6')
        m.addCommand("所有读取节点:显示所有缺帧", "wlf.asset.DropFrameCheck.show_dialog(True)")
        m.addCommand("所有读取节点:序列替单帧", "wlf.edit.replace_sequence()")
        m.addSeparator()
        m.addCommand("所有节点:删除未使用的节点","wlf.edit.delete_unused_nodes(message=True)")
        m.addCommand("所有节点:根据背板重命名", "wlf.edit.rename_all_nodes()" )
        m.addCommand("所有节点:根据背板分割文件", "wlf.edit.splitByBackdrop()")
        m.addCommand("所有节点:添加Dots变成90度","wlf.edit.nodes_add_dots(nuke.allNodes())")
        m.addCommand("所有节点:Gizmo转Group","wlf.edit.all_gizmo_to_group()")

    def _comp(menu):
        m = menu.addMenu('合成')
        m.addCommand('吾立方自动合成',"wlf.Comp()",icon='autocomp.png')
        m.addCommand('吾立方批量合成',"wlf.Comp.show_dialog()",icon='autocomp.png')
        m.addCommand('arnold预合成',"wlf.comp.precomp_arnold()",icon='autocomp.png')
        m.addCommand('色板\\/成果上传', 'import wlf.SceneTools;wlf.SceneTools.call_from_nuke()')

    def _cgtw(menu):

        m = menu.addMenu('CGTeamWork', icon='cgteamwork.png')
        m.addCommand('设置工程', "wlf.cgtw.CGTeamWork.ask_database()")
        m.addCommand('添加note', "wlf.cgtw.Shot().ask_add_note()")
        m.addCommand('上传nk文件', "wlf.cgtw.Shot().upload_nk_file()")
        m.addCommand('上传单帧', "wlf.cgtw.Shot().upload_image()")
        m.addCommand("批量下载", r'nukescripts.start(r"\\SERVER\scripts\NukePlugins\CGTeamWork工具\CGTW批量下载.bat")')

    def _create_node_menu():
        _plugin_path = '../../plugins'

        m = nuke.menu("Nodes")
        m = m.addMenu('吾立方', icon='Modify.png')
        os.chdir(os.path.dirname(__file__))
        
        create_menu_by_dir(m, _plugin_path)
        m.addCommand("吾立方网站", "nukescripts.start('http://www.wlf-studio.com/')")

    _menubar = nuke.menu("Nuke")

    _edit(_menubar)
    _comp(_menubar)
    _cgtw(_menubar)
    _create_node_menu()
    

def create_menu_by_dir(parent, dir):
    if not os.path.isdir(dir):
        return False
    _dir = os.path.abspath(dir)

    _order = lambda s: ('_0_' if os.path.isdir(os.path.join(_dir, s)) else '_1_') + s
    _listdir = os.listdir(_dir)
    _listdir.sort(key=_order)
    for i in _listdir:
        if i == 'icons':
            continue
        _abspath = os.path.join(_dir, i)
        _name, _ext = os.path.splitext(i)
        if os.path.isdir(_abspath):
            n = parent.addMenu(i, icon='{}.png'.format(i))            
            create_menu_by_dir(n, _abspath)
        elif _ext.lower() == '.gizmo':
            parent.addCommand(_name, 'nuke.createNode("{0}")'.format(_name), icon='{}.png'.format(_name))
            
def custom_autolabel(enable_text_style=True) :
    '''
    add addition information on Node in Gui
    '''
    a = autolabel().split( '\n' )[0]
    b = '\n'.join( autolabel().split( '\n' )[1:] )
    s = ''
    this = nuke.thisNode()
    if not this:
        return
    if this.Class() == 'Keyer' :
        s = '输入通道 : ' + nuke.value( 'this.input' )
    elif this.Class() == 'Read' :
        try:
            df = this['dropframes'].value()
        except NameError:
            df = ''

        if df :

            if enable_text_style:
                df = '\n<span style=\"color:red\">缺帧:' + df + '</span>'
            else:
                df = '\n缺帧:' + df
        else :
            df = ''

        if enable_text_style:
            s = '<span style=\"color:#548DD4;font-family:微软雅黑\"><b> 帧范围 :</b></span> '\
                '<span style=\"color:red\">' + nuke.value( 'this.first' ) + ' - ' + nuke.value( 'this.last' ) + '</span>'\
                + df
        else:
            s = '帧范围 :' + nuke.value( 'this.first' ) + ' - ' + nuke.value( 'this.last' ) + df
    elif this.Class() == 'Shuffle' :
        ch = dict.fromkeys( [ 'in', 'in2', 'out', 'out2'], '' )
        for i in ch.keys() :
            v = nuke.value( 'this.' + i)
            if v != 'none':
                ch[ i ] = v + ' '
        s = ( ch[ 'in' ] + ch[ 'in2' ] + '-> ' + ch[ 'out' ] + ch[ 'out2' ] ).rstrip( ' ' )
    else:
        return

    # join result
    if s :
        result = '\n'.join( [ a, s, b ] )
    elif b:
        result = '\n'.join( [ a, b ] )
    else :
        result = a
    result = result.rstrip( '\n' )
    return result

