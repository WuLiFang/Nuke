import nuke


def nodePresetsStartup():
    nuke.setPreset(
        "AddChannels", "depth", {"channels": "depth", "color": "1", "selected": "true"}
    )
    nuke.setPreset(
        "Camera2",
        "Camera_3DEnv_1",
        {
            "suppress_dialog": "true",
            "note_font": "\xe5\xbe\xae\xe8\xbd\xaf\xe9\x9b\x85\xe9\xbb\x91",
            "selected": "true",
            "label": "[knob this.xpos 0]\n[knob this.ypos 0]\n[knob this.name Camera_3DEnv_1]",
            "read_from_file": "true",
            "frame_rate": "25",
        },
    )
    nuke.setPreset(
        "ChannelMerge",
        "depth.z",
        {
            "A": "depth.Z",
            "output": "depth.Z",
            "operation": "min",
            "B": "depth.Z",
            "selected": "true",
        },
    )
    nuke.setPreset(
        "Copy", "depth.Z", {"to0": "depth.Z", "selected": "true", "from0": "depth.Z"}
    )
    nuke.setPreset(
        "Crop",
        "root.format",
        {
            "box": "0 0 {root.format.w} {root.format.h}",
            "indicators": "2",
            "reformat": "true",
            "selected": "true",
            "crop": "false",
        },
    )
    nuke.setPreset(
        "EXPTool",
        "LightFlicker",
        {
            "blue": "{green}",
            "random": "{(random(frame/(1/speed))-0.5)/(1/amplitude)}",
            "selected": "true",
            "smooth": "5.6",
            "lightRandom": "{this.random2.integrate(frame-subSmooth,frame+subSmooth)/(2*subSmooth)}",
            "label": "Light Flicker",
            "random2": "{this.random.integrate(frame-this.smooth,frame+this.smooth)/(2*this.smooth)}",
            "green": "{red}",
            "amplitude": "0.22",
            "indicators": "2",
            "speed": "2",
            "subSmooth": "1.3",
            "red": "{this.lightRandom}",
        },
    )
    nuke.setPreset(
        "Expression",
        "SaturationToRGB",
        {
            "expr0": "(max(r,g,b)-min(r,g,b))/max(r,g,b)",
            "channel0": "rgb",
            "selected": "true",
            "label": "SaturationToRGB",
        },
    )
    nuke.setPreset(
        "Expression",
        "Depth:NukeToRedshift",
        {
            "expr0": "(z==0)?99999:1/z*0.0001",
            "channel0": "depth",
            "selected": "true",
            "label": "Depth:NukeToRedshift",
        },
    )
    nuke.setPreset(
        "Expression",
        "Depth:RedshiftToNuke",
        {
            "expr0": "(z==0)?0:1/(z*10000)",
            "channel0": "depth",
            "selected": "true",
            "label": "Depth:RedshiftToNuke",
        },
    )
    nuke.setPreset(
        "Expression",
        "UV",
        {
            "postage_stamp": "true",
            "expr0": "(cx+1)/2",
            "expr1": "(cy+1)/2",
            "label": "UV",
        },
    )
    nuke.setPreset(
        "Merge2",
        "DepthMerge",
        {
            "Achannels": "depth",
            "output": "depth",
            "operation": "min",
            "Bchannels": "depth",
            "selected": "true",
        },
    )
    nuke.setPreset(
        "Merge2",
        "AO",
        {
            "screen_alpha": "true",
            "operation": "multiply",
            "selected": "true",
            "label": "AO",
        },
    )
    nuke.setPreset(
        "Merge2",
        "LayerCopy",
        {
            "Achannels": "BumpNormals",
            "output": "{{Achannels}}",
            "operation": "copy",
            "Bchannels": "{{Achannels}}",
            "selected": "true",
        },
    )
    nuke.setPreset(
        "Shuffle", "DepthToAlpha", {"selected": "true", "out": "alpha", "in": "depth"}
    )
    nuke.setPreset(
        "SoftClip",
        "Log_min:0",
        {"conversion": "logarithmic compress", "softclip_min": "0", "selected": "true"},
    )
    nuke.setPreset(
        "Transform",
        "ToCenter",
        {
            "indicators": "2",
            "label": "ToCenter",
            "translate": "{width/2-center.x} {height/2-center.y}",
            "selected": "true",
            "center": "1002 778",
        },
    )
    nuke.setPreset(
        "TransformGeo",
        "inputToThis",
        {
            "translate": "24.25000191 9.119999886 -3.639999151",
            "selected": "true",
            "rotate": "26.93956895 -46.47709455 13.99319297",
            "label": "[input this 2 Camera1]",
        },
    )
    nuke.setPreset(
        "TransformGeo",
        "inputPivot",
        {
            "indicators": "2",
            "pivot": "{input.translate} {input.translate} {input.translate}",
            "selected": "true",
            "rotate": "0 45 0",
            "note_font": "\xe5\xbe\xae\xe8\xbd\xaf\xe9\x9b\x85\xe9\xbb\x91",
        },
    )
    nuke.setPreset(
        "Write",
        "ScriptName.mov",
        {
            "beforeRender": "file = nuke.tcl('eval list {'+nuke.thisNode()[\"file\"].value()+'}');\nabsolutePath = os.path.splitdrive(file)[0];\nproject_directory = nuke.tcl('eval list {'+nuke.root()[\"project_directory\"].value()+'}');\npathHead = '' if absolutePath else project_directory+'/';\ntarget = pathHead+os.path.dirname(file)\nif os.path.exists(target):\n    pass;\nelse:\n    os.makedirs(target);\n",
            "checkHashOnRead": "false",
            "colorspace": "sRGB",
            "file_type": "mov",
            "file": "mov/[lindex [split [basename [value root.name]] .] 0].mov",
            "indicators": "2",
            "mov.meta_codec": "apch",
            "mov.mov64_bitrate": "20000",
            "mov.mov64_codec": "apch",
            "mov.mov64_fps": "{root.fps}",
            "proxy": "mov/[lindex [split [basename [value root.name]] .] 0]_proxy.mov",
            "version": "3",
        },
    )
    nuke.setPreset(
        "Write",
        "InputName.jpg",
        {
            "checkHashOnRead": "false",
            "file_type": "jpeg",
            "beforeRender": "file = nuke.tcl('eval list {'+nuke.thisNode()[\"file\"].value()+'}');\nabsolutePath = os.path.splitdrive(file)[0];\nproject_directory = nuke.tcl('eval list {'+nuke.root()[\"project_directory\"].value()+'}');\npathHead = '' if absolutePath else project_directory+'/';\ntarget = pathHead+os.path.dirname(file)\nif os.path.exists(target):\n    pass;\nelse:\n    os.makedirs(target);\n",
            "selected": "true",
            "jpeg._jpeg_quality": "1",
            "version": "3",
            "proxy": "images/[lindex [split [basename [metadata input/filename]] .] 0]_proxy.jpg",
            "file": "images/[lindex [split [basename [metadata input/filename]] .] 0].jpg",
        },
    )
    nuke.setPreset(
        "Write",
        "ScriptName.jpg_SingleFrame",
        {
            "checkHashOnRead": "false",
            "file_type": "jpeg",
            "beforeRender": "file = nuke.tcl('eval list {'+nuke.thisNode()[\"file\"].value()+'}');\nabsolutePath = os.path.splitdrive(file)[0];\nproject_directory = nuke.tcl('eval list {'+nuke.root()[\"project_directory\"].value()+'}');\npathHead = '' if absolutePath else project_directory+'/';\ntarget = pathHead+os.path.dirname(file)\nif os.path.exists(target):\n    pass;\nelse:\n    os.makedirs(target);\n",
            "selected": "true",
            "jpeg._jpeg_quality": "1",
            "version": "15",
            "use_limit": "true",
            "proxy": "images/[lindex [split [basename [value root.name]] .] 0]_proxy.%04d.jpg",
            "file": "images/[lindex [split [basename [value root.name]] .] 0].%04d.jpg",
            "indicators": "2",
            "last": "{first}",
            "first": '{"\\[value root.first_frame]"}',
        },
    )
    nuke.setPreset(
        "Write",
        "InputName.####.png",
        {
            "channels": "rgba",
            "checkHashOnRead": "false",
            "file_type": "png",
            "beforeRender": "file = nuke.tcl('eval list {'+nuke.thisNode()[\"file\"].value()+'}');\nabsolutePath = os.path.splitdrive(file)[0];\nproject_directory = nuke.tcl('eval list {'+nuke.root()[\"project_directory\"].value()+'}')+'/';\npathHead = '' if absolutePath else project_directory;\nos.makedirs(pathHead+os.path.dirname(file));\n",
            "selected": "true",
            "label": '<font size="3" color =#548DD4><b> Frame range :</b></font> <font color = red>[value first] - [value last] </font>',
            "version": "6",
            "use_limit": "true",
            "proxy": "images/[lindex [split [basename [metadata input/filename]] .] 0]/[lindex [split [basename [metadata input/filename]] .] 0]_proxy.%04d.png",
            "file": "images/[lindex [split [basename [metadata input/filename]] .] 0]/[lindex [split [basename [metadata input/filename]] .] 0].%04d.png",
            "indicators": "2",
            "last": '{"\\[python nuke.thisNode().input(0).lastFrame()]"}',
            "first": '{"\\[python nuke.thisNode().input(0).firstFrame()]"}',
            "png.datatype": "16 bit",
        },
    )
    nuke.setPreset(
        "Write",
        "InputName.mov",
        {
            "beforeRender": "file = nuke.tcl('eval list {'+nuke.thisNode()[\"file\"].value()+'}');\nabsolutePath = os.path.splitdrive(file)[0];\nproject_directory = nuke.tcl('eval list {'+nuke.root()[\"project_directory\"].value()+'}');\npathHead = '' if absolutePath else project_directory+'/';\ntarget = pathHead+os.path.dirname(file)\nif os.path.exists(target):\n    pass;\nelse:\n    os.makedirs(target);\n",
            "checkHashOnRead": "false",
            "colorspace": "sRGB",
            "file_type": "mov",
            "file": "mov/[lindex [split [basename [metadata input/filename]] .] 0].mov",
            "indicators": "2",
            "mov.meta_codec": "apch",
            "mov.mov64_bitrate": "20000",
            "mov.mov64_codec": "apch",
            "mov.mov64_fps": "{root.fps}",
            "proxy": "mov/proxy/[lindex [split [basename [metadata input/filename]] .] 0].mov",
            "version": "3",
        },
    )
    nuke.setPreset(
        "ZDefocus2",
        "direct",
        {
            "z_channel": "depth3split.focus",
            "blur_dof": "false",
            "selected": "true",
            "legacy_resize_mode": "false",
            "math": "direct",
            "show_legacy_resize_mode": "false",
            "max_size": "6",
            "size": "10",
        },
    )
    nuke.setPreset(
        "GodRays",
        "Aberration",
        {
            "selected": "true",
            "tile_color": "0xff8200ff",
            "maskChannelInput": "-rgba.alpha",
            "label": "Aberration",
            "channels": "-rgba.red -rgba.green rgba.blue none",
            "translate": "3 -2",
        },
    )
    nuke.setPreset(
        "VectorBlur2",
        "MotionVectors -xxx~xxx",
        {
            "scale": "1",
            "blur_uv": "uniform",
            "uv": "MotionVectors",
            "soft_lines": "true",
        },
    )
    nuke.setPreset(
        "VectorBlur2",
        "motion 0~1",
        {
            "scale": "30",
            "uv_offset": "-0.5",
            "uv": "motion",
            "blur_uv": "uniform",
            "soft_lines": "true",
        },
    )
    nuke.setPreset(
        "Expression",
        "1 \\/ MotionVectors",
        {
            "note_font": "\xe5\xbe\xae\xe8\xbd\xaf\xe9\x9b\x85\xe9\xbb\x91",
            "selected": "true",
            "channel1": "-MotionVectors.red MotionVectors.green -MotionVectors.blue -MotionVectors.alpha",
            "channel2": "-rgba.red -rgba.green -rgba.blue none",
            "expr0": "(MotionVectors.red == 0) ? 1 / MotionVectors.red * 1000 : 0",
            "expr1": "(MotionVectors.green == 0) ? 1 / MotionVectors.green * 1000 : 0",
            "gl_color": "0xff833200",
            "channel0": "MotionVectors.red -MotionVectors.green -MotionVectors.blue -MotionVectors.alpha",
        },
    )
