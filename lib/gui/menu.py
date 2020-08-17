# -*- coding: UTF-8 -*-
"""Setup UI."""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import webbrowser
from itertools import chain

import nuke
import nukescripts  # type: ignore
import six

import asset
import cgtwn_panels
import cgtwq
import comp
import comp.panels
import edit
import edit.motion_distort
import edit.rotopaint_dopesheet
import edit.script_use_seq
import edit.script_use_seq.panels
import edit_panels
import enable_later
import nuketools
import orgnize
import scanner
import splitexr
from nuketools import utf8

WINDOW_CONTEXT = 0
APPLICATION_CONTEXT = 1
DAG_CONTEXT = 2

LOGGER = logging.getLogger('com.wlf.ui')
RESOURCE_DIR = os.path.abspath(os.path.join(__file__, '../../../'))


def add_menu():
    """Add menu for commands and nodes."""

    LOGGER.info('添加菜单')

    def _(*args, **kwargs):
        args = (i.encode('utf-8') if isinstance(i, six.text_type) else i
                for i in args)
        kwargs = tuple({k: v.encode('utf-8') if isinstance(v, six.text_type) else v
                        for k, v in kwargs.items()}.items())
        return (args, kwargs)

    def _autocomp():
        try:
            comp.Comp().create_nodes()
        except comp.FootageError:
            nuke.message(utf8('请先导入素材'))

    def _open_help():
        help_page = os.path.join(
            RESOURCE_DIR, 'docs/build/html/index.html')
        webbrowser.open(help_page)

    def concat_list(a, b):
        ret = []
        ret.extend(a)
        ret.extend(b)
        return ret

    all_menu = [
        {_('编辑'): [
            _('同时编辑多个节点', lambda: edit_panels.MultiEdit().show(), 'F2'),
            _('RotoPaint摄影表', lambda: edit.rotopaint_dopesheet.Panel(
                nuketools.selected_node()).show(), 'SHIFT+R'),
            _('分离图层', lambda: edit.split_layers(nuketools.selected_node()),
              'F3', icon="SplitLayers.png"),
            _("分离rgba",
              lambda: edit.shuffle_rgba(nuketools.selected_node()), 'SHIFT+F3'),
            _("重命名PuzzleMatte",
              lambda: edit_panels.ChannelsRename().show(), 'F4'),
            _("标记为稍后启用",
              lambda: enable_later.mark_enable(
                  nuke.selectedNodes()), 'SHIFT+D'),
            _('输出当前帧png',
              lambda: comp.render_png(nuke.selectedNodes(), show=True),
              'SHIFT+F7'),
            _("设置帧范围",
              edit.dialog_set_framerange),
            _('转换为相对路径',
              lambda: edit.use_relative_path(
                  nuke.selectedNodes()), icon="utilitiesfolder.png"),
            None,
            _("禁用所有稍后启用节点",
              lambda: enable_later.marked_nodes().disable(), 'CTRL+SHIFT+D'),
            _("修正读取错误", asset.fix_read, 'F6'),
            _("Reload所有", edit.reload_all_read_node),
            _("检查缺帧", lambda: asset.warn_missing_frames(show_ok=True)),
            _("检查素材更新", lambda: asset.warn_mtime(show_ok=True)),
            _("转换单帧为序列",
              edit.replace_sequence),
            _("匹配抽帧",
              edit.match_drop_frame.show_dialog),
            {
                _('转换为序列工程'): [
                    _('对当前工程执行', edit.script_use_seq.execute),
                    _('对文件夹执行',
                      lambda: edit.script_use_seq.panels.BatchPanel().showModalDialog()),
                    _('设置',
                      lambda: edit.script_use_seq.panels.ConfigPanel().showModalDialog()),
                ]
            },
            _("创建 MotionDistort",
              edit.motion_distort.show_motion_distort_dialog),
            {_('最佳实践'): [
                _("清理无用节点",
                  lambda: edit.delete_unused_nodes(message=True)),
                _("合并重复读取节点",
                  edit.remove_duplicated_read),
                _("Glow节点不使用mask",
                  edit.best_practice.glow_no_mask)
            ]},
            {_('整理'): [
                _("整理所选节点(竖式摆放)",
                  lambda: orgnize.autoplace(nuke.selectedNodes()),
                  "L", shortcutContext=DAG_CONTEXT),
                _("所有Gizmo转Group",
                  edit.all_gizmo_to_group),
                _("根据背板重命名所有节点",
                  orgnize.rename_all_nodes),
                _("节点添加Dots变成90度",
                  lambda: orgnize.nodes_add_dots(nuke.selectedNodes())),
                _("所有节点添加Dots变成90度",
                  lambda: orgnize.nodes_add_dots(nuke.allNodes()))
            ]}
        ]},
        {_('合成'): chain(
            [
                _('自动合成', _autocomp, icon='autocomp.png'),
                _('自动合成设置',
                  lambda: comp.panels.CompConfigPanel(

                  ).showModalDialog(), icon='autocomp.png'),
                _('自动预合成',
                  nuketools.undoable_func('自动预合成')(
                      lambda: comp.Precomp(nuke.selectedNodes())),
                  'F1',
                  shortcutContext=DAG_CONTEXT,
                  icon='autocomp.png'),
            ],
            (_('{} 预合成'.format(v.name),
               nuketools.undoable_func('{} 预合成'.format(v.name))(
                   lambda: comp.Precomp(nuke.selectedNodes(), renderer=k)),
               icon='autocomp.png') for k, v in comp.precomp.RENDERER_REGISTRY.items()),
        )},
        {_('工具'): [
            _('批量自动合成', lambda: comp.panels.BatchCompPanel().showModalDialog(),
              icon='autocomp.png'),
            _('扫描空文件夹', scanner.call_from_nuke),
            _('分离exr', splitexr.Dialog.show),
            _("分割当前文件(根据背板)", orgnize.split_by_backdrop)
        ]},
        {_('帮助'): [
            _('吾立方插件 文档', _open_help),
            _("吾立方网站", lambda: webbrowser.open('http://www.wlf-studio.com/'))
        ]}
    ]
    if cgtwq.DesktopClient().executable():
        all_menu.insert(
            -2,
            {_('CGTeamWork', icon='cgteamwork.png'): [
                _('登录', cgtwn_panels.dialog_login),
                _('创建项目文件夹', cgtwn_panels.dialog_create_dirs),
                _('上传工具', lambda: nukescripts.panels.restorePanel(
                    'com.wlf.uploader')),
            ]}
        )

    if getattr(nuke, 'startPerformanceTimers'):
        all_menu.insert(
            -1,
            {_('性能监控'): [
                _('开始', nuke.startPerformanceTimers),
                _('结束', nuke.stopPerformanceTimers),
                _('重置', nuke.resetPerformanceTimers),
            ], })

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
    _plugin_path = '../../../plugins'

    m = nuke.menu("Nodes")
    m = m.addMenu('吾立方'.encode('utf-8'), icon='Modify.png')
    create_menu_by_dir(m, os.path.abspath(
        os.path.join(__file__, _plugin_path)))


def create_menu_by_dir(parent, dir_):
    """Create menus by given folder structrue."""

    if not os.path.isdir(dir_):
        return False
    _dir = os.path.abspath(dir_)

    def _order(name):
        return ('_0_' if os.path.isdir(
            os.path.join(_dir, name)) else '_1_') + name

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


def panel_show(keyword):
    """Show control panel for matched nodes."""

    nodes = sorted((n for n in nuke.allNodes()
                    if keyword in n.name()
                    and not nuke.numvalue('{}.disable'.format(n.name()), 0)),
                   key=lambda n: n.name(),
                   reverse=True)
    for n in nodes:
        n.showControlPanel()
