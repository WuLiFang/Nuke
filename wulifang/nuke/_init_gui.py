# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals

import webbrowser

import nuke

import wulifang
import wulifang.license
import wulifang.nuke
from wulifang.nuke.infrastructure import pyblish
from wulifang.nuke.infrastructure.autolabel_service import AutolabelService
from wulifang.vendor import cgtwq_uploader
from wulifang.vendor.cgtwq import desktop as cgtw
from wulifang._util import cast_str, workspace_path, assert_not_none
from wulifang.nuke._util import (
    gizmo_to_group,
    NodeList,
    selected_node,
    Panel,
    reload_node,
    iter_deep_all_nodes,
    undoable,
)
from wulifang.nuke.infrastructure.cgteamwork import (
    dialog_create_dirs as cgt_create_dirs_dialog,
)
from wulifang import (
    _find_empty_dir,
)
from ._init import skip_gui as _skip
from ._pack_project import pack_project
from ._find_max_bbox_node import show_max_bbox_node
from ._rename_all_nodes_by_backdrop import rename_all_nodes_by_backdrop
from . import (
    _add_dot_on_node_connection,
    _aov_assemble,
    _auto_place,
    _create_color_replace,
    _create_motion_distort,
    _drop_data,
    _enable_later,
    _file_mtime_check,
    _fix_cryptomatte_name_lost,
    _fix_read,
    _fix_unicode_decode_error,
    _fixed_tab_stats_path,
    _jump_to_wlf_write_frame,
    _match_drop_frame,
    _missing_frame_check,
    _multi_node_edit,
    _node_menu,
    _node_suggestion,
    _preference,
    _project_settings,
    _prune_node,
    _python2_project_warning,
    _random_gl_color,
    _remove_duplicated_read,
    _rename_channels,
    _render_png,
    _replace_file_path,
    _replace_glow_mask_with_width,
    _replace_with_relative_path,
    _replace_with_sequence_path,
    _rotopaint_dopesheet,
    _rotopaint_motion_distort,
    _rotopaint_uv_map,
    _split_color,
    _split_exr,
    _split_file_by_backdrop,
    _split_layer_group_by_re,
    _split_layers,
    _split_psd_layers,
    _split_rgba,
    _generate_proxy,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Callable, Protocol, Any
    from . import _types

    class _MenuItem(Protocol):
        def create(self, menu):
            # type: (nuke.Menu) -> None
            pass

else:
    _MenuItem = object


def _reload():
    import wulifang.nuke

    wulifang.nuke.reload()


def _selected_gizmo_to_group():
    nodes = [i for i in nuke.selectedNodes() if isinstance(i, nuke.Gizmo)]
    if not nodes:
        nuke.message(cast_str("未选中任何 Gizmo"))
        return

    for n in nodes:
        gizmo_to_group(n)


def _init_cgtw():
    exe = cgtw.default_executable()
    if not exe:
        return
    Panel.register(
        "com.wlf.uploader",
        "上传至 CGTeamwork",
        cgtwq_uploader.Dialog,
    )
    _Menu(
        "CGTeamwork",
        (
            _Command(
                "按镜头创建文件夹",
                cgt_create_dirs_dialog.dialog_create_dirs,
            ),
            _Command(
                "上传及提交...",
                lambda: Panel.restore("com.wlf.uploader"),
            ),
        ),
        icon="cgteamwork.png",
    ).create(nuke.menu(cast_str("Nuke")))


def _must_selected_nodes():
    v = nuke.selectedNodes()
    if not v:
        nuke.message(cast_str("请先选择节点"))
        raise ValueError("no selected nodes")
    return v


class _g:
    init_once = False


class _Command(_MenuItem):
    # shortcut context
    SC_WINDOW = 0
    SC_APPLICATION = 1
    SC_DAG = 2

    def __init__(
        self,
        _name,  # type: Text
        _command,  # type: Callable[[], Any]
        shortcut="",  # type: Text
        shortcut_context=0,  # type:  int
        icon="",  # type: Text
        readonly=False,  # type: bool
    ):
        # type: (...) -> None
        self.name = _name
        self.command = _command
        self.shortcut = shortcut
        self.shortcut_context = shortcut_context
        self.icon = icon
        self.readonly = readonly

    def create(self, menu):
        # type: (nuke.Menu) -> None
        menu.addCommand(
            cast_str(self.name),
            self.command,
            shortcut=cast_str(self.shortcut),
            shortcutContext=self.shortcut_context,
            icon=cast_str(self.icon),
            readonly=self.readonly,
        )

        def cleanup():
            menu.removeItem(cast_str(self.name))

        wulifang.cleanup.add(cleanup)


class _Separator(_MenuItem):
    def create(self, menu):
        # type: (nuke.Menu) -> None
        item = menu.addSeparator()

        def cleanup():
            menu.removeItem(item.name())

        wulifang.cleanup.add(cleanup)


class _Menu(_MenuItem):
    def __init__(
        self,
        name,  # type: Text
        items,  # type: tuple[_MenuItem, ...]
        icon="",  # type: Text
    ):
        # type: (...) -> None
        self.name = name
        self.items = items
        self.icon = icon

    def obtain(self, parent):
        # type: (nuke.Menu) -> nuke.Menu
        m = parent.menu(cast_str(self.name))
        if isinstance(m, nuke.Menu):
            return m
        m = parent.addMenu(
            cast_str(self.name),
            icon=cast_str(self.icon),
        )

        def cleanup():
            # use `m` cause crash
            parent.removeItem(cast_str(self.name))

        wulifang.cleanup.add(cleanup)
        return m

    def create(self, menu):
        # type: (nuke.Menu) -> None

        sub_menu = self.obtain(menu)
        for i in self.items:
            i.create(sub_menu)


class _LegacyCommandPlaceholder(_Command):
    def __init__(
        self,
        name,  # type: Text
        shortcut="",  # type: Text
        icon="",  # type: Text
    ):
        super(_LegacyCommandPlaceholder, self).__init__(
            name,
            lambda: nuke.message(cast_str("此功能暂时只在 Nuke 12 及以下版本可用")),
            shortcut=shortcut,
            icon=icon,
        )

    def create(self, menu):
        # type: (nuke.Menu) -> None
        if nuke.NUKE_VERSION_MAJOR <= 12:
            return
        super(_LegacyCommandPlaceholder, self).create(menu)


def _aov_assemble_by_spec(spec):
    # type: (_types.AOVSpec) -> _Command
    return _Command(
        "%s #MERGE-ZZ-AOV-%s" % (spec.name, spec.name.upper()),
        lambda: _aov_assemble.assemble(_must_selected_nodes(), spec),
        icon="Merge.png",
    )


def _init_menu():
    rootMenu = nuke.menu(cast_str("Nuke"))
    nodeMenu = _Menu(
        "吾立方",
        (),
        icon="wulifang-dark.png",
    ).obtain(nuke.menu(cast_str("Nodes")))
    nodeCommandMenu = _Menu("命令", ()).obtain(nodeMenu)
    nodeCommandMenu.setVisible(False)
    for i in (
        _Menu(
            "文件",
            (
                _Command("打包 #DB", pack_project),
                _Command(
                    "触发所有节点的 reload 按钮 #CFSYJDD-RELOAD-AN",
                    lambda: [reload_node(i) for i in iter_deep_all_nodes()],
                ),
                _Command(
                    "清理无用节点 #QLWYJD",
                    lambda: _prune_node.show(_prune_node.prune(nuke.allNodes())),
                ),
                _Command(
                    "修复字符解码错误(UnicodeDecodeError) #XFZFJMCW",
                    lambda: _fix_unicode_decode_error.fix_unicode_decode_error(),
                ),
                _Menu(
                    "性能计时",
                    (
                        _Command("开始 #KS-XNJS", nuke.startPerformanceTimers),
                        _Command("结束 #JS-XNJS", nuke.stopPerformanceTimers),
                        _Command("重置 #CZ-XNJS", nuke.resetPerformanceTimers),
                    ),
                ),
                _Separator(),
                _Command(
                    "Read,DeepRead: 检查缺帧 #JCQZ",
                    lambda: _missing_frame_check.show(
                        _missing_frame_check.find(nuke.allNodes()),
                        verbose=True,
                    ),
                    icon="Read.png",
                ),
                _Command(
                    "Read,DeepRead: 检查素材更新 #JCSCGX",
                    lambda: _file_mtime_check.show(
                        nuke.allNodes(),
                        verbose=True,
                    ),
                    icon="Read.png",
                ),
                _Command(
                    "Read: 移除重复节点 #YCCFJD",
                    lambda: _remove_duplicated_read.show(
                        _remove_duplicated_read.remove()
                    ),
                    icon="Read.png",
                ),
                _Command(
                    "Glow: 用 width 通道代替 mask #Y-WIDTH-TDDT-MASK",
                    lambda: _replace_glow_mask_with_width.replace(),
                    icon="Glow.png",
                ),
                _Command(
                    "Backdrop: 重命名内部节点 #CMMNBJD",
                    rename_all_nodes_by_backdrop,
                    icon="Backdrop.png",
                ),
                _Command(
                    "Backdrop: 拆分文件... #CFWJ",
                    _split_file_by_backdrop.dialog,
                    icon="Backdrop.png",
                ),
            ),
        ),
        _Menu(
            "编辑",
            (
                _Command(
                    "同时编辑多个节点 #TSBJDGJD",
                    lambda: _multi_node_edit.MultiNodeEdit(
                        _must_selected_nodes()
                    ).show(),
                    shortcut="F2",
                ),
                _Command("查找最大 BBox #CZZD-BBOX", show_max_bbox_node, readonly=True),
                _Command(
                    "替换文件路径... #THWJLJ",
                    lambda: _replace_file_path.dialog(_must_selected_nodes()),
                    icon="Read.png",
                ),
                _Command(
                    "转换为序列路径 #ZHWXLLJ",
                    lambda: _replace_with_sequence_path.show(
                        _replace_with_sequence_path.replace(_must_selected_nodes())
                    ),
                    icon="Read.png",
                ),
                _Command(
                    "转换为相对路径 #ZHWXDLJ",
                    lambda: _replace_with_relative_path.show(
                        _replace_with_relative_path.replace(_must_selected_nodes())
                    ),
                    icon="Read.png",
                ),
                _Command(
                    "自动摆放(竖式) #ZDBF-SS",
                    undoable("自动摆放")(
                        lambda: _auto_place.auto_place(_must_selected_nodes())
                    ),
                    shortcut="L",
                    shortcut_context=_Command.SC_DAG,
                ),
                _Menu(
                    "稍后启用",
                    (
                        _Command(
                            "标记 #BJ-SHQY",
                            lambda: _enable_later.mark(_must_selected_nodes()),
                            shortcut="SHIFT+D",
                            shortcut_context=_Command.SC_DAG,
                        ),
                        _Command(
                            "禁用已标记 #JYYBJ-SHQY",
                            lambda: NodeList(_enable_later.nodes()).disable(),
                            shortcut="CTRL+SHIFT+D",
                            shortcut_context=_Command.SC_DAG,
                        ),
                        _Command(
                            "启用已标记 #QYYBJ-SHQY",
                            lambda: NodeList(_enable_later.nodes()).enable(),
                        ),
                        _Command(
                            "选择已标记 #XZYBJ-SHQY",
                            lambda: NodeList(_enable_later.nodes()).select(),
                        ),
                    ),
                ),
                _Separator(),
                _Command(
                    "Read,DeepRead: 修复错误 #XFCW",
                    lambda: _fix_read.show(
                        _fix_read.fix(_must_selected_nodes()),
                        verbose=True,
                    ),
                    icon="Read.png",
                ),
                _Command(
                    "Read: 生成代理 #SCDL",
                    lambda: _generate_proxy.dialog(_must_selected_nodes()),
                    icon="Read.png",
                ),
                _Command(
                    "Cryptomatte: 修复名称丢失 #XFMCDS",
                    lambda: _fix_cryptomatte_name_lost.show(
                        _fix_cryptomatte_name_lost.fix(_must_selected_nodes()),
                        verbose=True,
                    ),
                    icon="Cryptomatte.png",
                ),
                _Menu(
                    "Merge: 组装 AOV",
                    (
                        _Command(
                            "自动检测 #MERGE-ZZ-AOV-ZDJC",
                            lambda: _aov_assemble.assemble(_must_selected_nodes()),
                            icon="Merge.png",
                            shortcut="F1",
                        ),
                    )
                    + tuple(_aov_assemble_by_spec(i) for i in _aov_assemble.all_spec()),
                    icon="Merge.png",
                ),
                _Command(
                    "Shuffle: 拆分图层 #CFTC",
                    lambda: tuple(_split_layers.split(selected_node())),
                    icon="Shuffle.png",
                ),
                _Command(
                    "Shuffle: 拆分 rgba #CF-RGBA",
                    lambda: tuple(_split_rgba.split(selected_node())),
                    icon="Shuffle.png",
                ),
                _Command(
                    "Shuffle: 正则拆分图层组... #ZZCFTCZ",
                    lambda: _split_layer_group_by_re.dialog(_must_selected_nodes()),
                    icon="Shuffle.png",
                ),
                _Command(
                    "ColorKeyer: 拆分颜色 #CFYS",
                    lambda: tuple(
                        tuple(_split_color.split(i)) for i in _must_selected_nodes()
                    ),
                    icon="ColorKeyer.png",
                ),
                _Command(
                    "ColorReplace: 替换颜色 #THYS",
                    lambda: tuple(
                        tuple(_create_color_replace.create(i))
                        for i in _must_selected_nodes()
                    ),
                    icon="ColorReplace.svg",
                ),
                _Command(
                    "Copy: 重命名通道... #CMMTD",
                    lambda: _rename_channels.RenameChannels(selected_node()).show(),
                    icon="ShuffleCopy.png",
                ),
                _Command(
                    "TimeWarp: 匹配抽帧... #PPCZ",
                    lambda: _match_drop_frame.dialog(selected_node()),
                    icon="TimeWarp.png",
                ),
                _Command(
                    "IDistort: 创建运动扭曲... #CJYDNQ",
                    lambda: _create_motion_distort.dialog(),
                    icon="IDistort.png",
                ),
                _Command(
                    "RotoPaint: 摄影表... #SYB",
                    lambda: _rotopaint_dopesheet.Panel(selected_node()).show(),
                    icon="RotoPaint.png",
                ),
                _Command(
                    "RotoPaint: 运动扭曲... #YDNQ",
                    lambda: _rotopaint_motion_distort.dialog(_must_selected_nodes()),
                    icon="RotoPaint.png",
                ),
                _Command(
                    "RotoPaint: UV 映射 #UV-YS",
                    lambda: _rotopaint_uv_map.create(_must_selected_nodes()),
                    icon="RotoPaint.png",
                ),
                _Command(
                    "Gizmo: 转为 Group #ZW-GROUP",
                    _selected_gizmo_to_group,
                    icon="Group.png",
                ),
                _Command(
                    "Write: 输出当前帧 PNG #SCDQZ-PNG",
                    lambda: _render_png.render(_must_selected_nodes(), open_dir=True),
                    shortcut="SHIFT+F7",
                    icon="Write.png",
                ),
                _Command(
                    "Dot: 使输入连线变为 90 度 #SSRLXBW90D",
                    lambda: _add_dot_on_node_connection.add(_must_selected_nodes()),
                    icon="Dot.png",
                ),
            ),
        ),
        _Menu(
            "工具",
            (
                _Command(
                    "查找空文件夹... #CZKWJJ",
                    lambda: _find_empty_dir.dialog(),
                ),
                _Command(
                    "拆分 EXR... #CF-EXR",
                    lambda: _split_exr.dialog(),
                    icon="Write.png",
                ),
                _Command(
                    "批量替换文件路径... #PLTHWJLJ",
                    lambda: _replace_file_path.batch_dialog(),
                    icon="Read.png",
                ),
                _LegacyCommandPlaceholder(
                    "TODO: 批量转换为序列路径...",
                ),
                _LegacyCommandPlaceholder(
                    "TODO: 批量按素材名组装...",
                    icon="Merge.png",
                ),
            ),
        ),
        _Menu(
            "帮助",
            (
                _Command(
                    "吾立方插件文档 #WLFCJWD",
                    lambda: webbrowser.open(
                        workspace_path("docs/_build/html/index.html")
                    ),
                ),
                _Command(
                    "吾立方插件发布页 #WLFCJFBY",
                    lambda: webbrowser.open(
                        "https://github.com/WuLiFang/Nuke/releases"
                    ),
                ),
                _Command(
                    "重新加载吾立方插件 #CXJZWLFCJ",
                    _reload,
                    shortcut="Ctrl+Shift+F5",
                ),
            ),
        ),
    ):
        i.create(nodeCommandMenu)
        i.create(rootMenu)

    # Set old autoplace shortcut.
    try:
        (
            assert_not_none(
                assert_not_none(
                    assert_not_none(
                        nuke.menu(cast_str("Nuke")).findItem(cast_str("Edit"))
                    ).findItem(cast_str("Node"))
                ).findItem(cast_str("Autoplace"))
            ).setShortcut(cast_str("Ctrl+L"))
        )
    except AssertionError:
        pass


def init_gui():
    if _g.init_once or _skip():
        return
    wulifang.publish = pyblish.PublishService()
    autolabel = AutolabelService(wulifang.file)
    wulifang.cleanup.add(lambda: nuke.removeAutolabel(autolabel.autolabel))

    _fixed_tab_stats_path.init_gui()
    nuke.addAutolabel(autolabel.autolabel)
    _init_menu()
    _node_menu.init_gui()
    _project_settings.init_gui()
    _auto_place.init_gui()
    _enable_later.init_gui()
    _preference.init_gui()
    _drop_data.init_gui()
    _missing_frame_check.init_gui()
    _file_mtime_check.init_gui()
    _random_gl_color.init_gui()
    _jump_to_wlf_write_frame.init_gui()
    _node_suggestion.init_gui()
    _fix_unicode_decode_error.init_gui()
    _fix_cryptomatte_name_lost.init_gui()
    _split_psd_layers.init_gui()
    _python2_project_warning.init_gui()
    _init_cgtw()
    _g.init_once = True
