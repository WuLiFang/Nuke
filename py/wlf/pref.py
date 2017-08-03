# -*- coding=UTF-8 -*-
"""Custom nuke preference."""

import nuke


def set_knob_default():
    """Set nuke knob default when node create."""

    def _vectorblur2():
        nuke.knobDefault("VectorBlur2.uv", "motion")
        # nuke.knobDefault("VectorBlur2.blur_uv", "uniform")
        nuke.knobDefault("VectorBlur2.uv_offset", "0")
        nuke.knobDefault("VectorBlur2.scale", "1")
        nuke.knobDefault("VectorBlur2.soft_lines", "True")
        nuke.knobDefault("VectorBlur2.normalize", "True")

    def _root():
        nuke.knobDefault("Root.fps", "25")
        nuke.knobDefault("Root.format", "1920 1080 0 0 1920 1080 1 HD_1080")
        # nuke.knobDefault("Root.project_directory",
        #                  r"[python {os.path.join("
        #                  r"nuke.value('root.name', ''), '../'"
        #                  r").replace('\\', '/')}]")
        # nuke.knobDefault("Root.free_type_font_path", "//SERVER/scripts/NukePlugins/Fonts")

    def _zdefocus2():
        nuke.knobDefault("ZDefocus2.blur_dof", "0")
        nuke.knobDefault("ZDefocus2.math", "depth")

    _root()
    _vectorblur2()
    _zdefocus2()
    nuke.knobDefault("LayerContactSheet.showLayerNames", "1")
    nuke.knobDefault("note_font", '微软雅黑')
    nuke.knobDefault("Switch.which", "1")
    nuke.knobDefault("Viewer.input_process", "False")
    nuke.knobDefault("SoftClip.conversion", "3")
    nuke.knobDefault("PositionToPoints.P_channel", "P")
    nuke.knobDefault('Roto.cliptype', 'no clip')
    nuke.knobDefault('RotoPaint.cliptype', 'no clip')

    k = nuke.toNode('preferences')['UIFontSize']
    if k.value() == 11:
        k.setValue(12)


def add_preferences():
    """Add a prefrences panel."""

    pref = nuke.toNode('preferences')
    k = nuke.Tab_Knob('wlf_tab', '吾立方')
    pref.addKnob(k)

    def _remove_old():
        for k in ['wlf_lock_connection', 'wlf_tab']:
            try:
                pref.removeKnob(pref[k])
            except NameError:
                pass

    def _add_knob(k):
        _knob_tcl_name = 'preferences.{}'.format(k.name())
        if nuke.exists(_knob_tcl_name):
            k.setValue(pref[k.name()].value())
            pref.removeKnob(pref[k.name()])
        k.setFlag(nuke.ALWAYS_SAVE)
        pref.addKnob(k)

    k = nuke.String_Knob('wlf_artist', '制作人信息')
    k.setFlag(nuke.STARTLINE)
    _add_knob(k)

    k = nuke.Boolean_Knob('wlf_gizmo_to_group', '创建Gizmo时尝试转换为Group')
    k.setFlag(nuke.STARTLINE)
    _add_knob(k)

    k = nuke.Boolean_Knob('wlf_eval_proj_dir', '读取时工程目录自动转换为绝对路径')
    k.setValue(True)
    k.setFlag(nuke.STARTLINE)
    _add_knob(k)

    k = nuke.Text_Knob('wlf_on_script_save', '保存时')
    _add_knob(k)

    k = nuke.Boolean_Knob('wlf_autoplace', '自动摆放节点')
    k.setFlag(nuke.STARTLINE)
    _add_knob(k)

    k = nuke.Boolean_Knob('wlf_lock_connections', '锁定节点连接')
    k.setFlag(nuke.STARTLINE)
    _add_knob(k)

    k = nuke.Boolean_Knob('wlf_enable_node', '启用名称以 _enable_ 开头的节点')
    k.setValue(True)
    k.setFlag(nuke.STARTLINE)
    _add_knob(k)

    k = nuke.Boolean_Knob('wlf_jump_frame', '跳至_Write节点指定的帧')
    k.setValue(True)
    k.setFlag(nuke.STARTLINE)
    _add_knob(k)

    k = nuke.Text_Knob('wlf_on_script_close', '保存并退出时')
    _add_knob(k)

    k = nuke.Boolean_Knob('wlf_render_jpg', '渲染_Write节点单帧')
    k.setValue(True)
    k.setFlag(nuke.STARTLINE)
    _add_knob(k)

    k = nuke.Boolean_Knob('wlf_send_to_dir', '发送至渲染文件夹(Nuke渲染不支持中文路径)')
    k.setFlag(nuke.STARTLINE)
    _add_knob(k)

    k = nuke.File_Knob('wlf_render_dir', '')
    k.clearFlag(nuke.STARTLINE)
    _add_knob(k)

    k = nuke.Boolean_Knob('wlf_create_csheet', '生成色板(如果目录下有配置文件)')
    k.setFlag(nuke.STARTLINE)
    _add_knob(k)

    _remove_old()
