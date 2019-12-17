import os

import wlf.config


START_MESSAGE = '{:-^50s}'.format('SCRIPT USE SEQUENCE CONVERT START')


class Config(wlf.config.Config):
    default = {
        "seq_include": "Z:/CGteamwork_Test/MT2/shot_work/Render/EP00/*/eps/*/*.exr",
        "seq_exclude": "**/mov/*",
        "is_auto_frame_range": True,
        "use_wlf_write": True,
        "override_project_directory": "[python {nuke.script_directory()}]",
        "input_dir": "",
        "output_dir": "",
    }
    path = os.path.expanduser('~/.nuke/wlf.script_use_seq.json')
