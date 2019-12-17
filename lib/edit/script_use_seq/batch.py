# -*- coding=UTF-8 -*-
"""Batch runner.  """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import io
import os
import subprocess
import tempfile
import webbrowser

import nuke
import six

from wlf.decorators import run_async
from wlf.path import Path
from wlf.progress import progress

from . import __main__, files
from .config import Config


@run_async
def run(input_dir, output_dir):
    cfg = Config()
    temp_fd, temp_fp = tempfile.mkstemp("-script_use_seq")
    try:
        for _ in progress(["获取文件列表……"], '匹配文件'):
            footages = files.search(
                include=cfg['seq_include'].splitlines(),
                exclude=cfg['seq_exclude'].splitlines())
        with io.open(temp_fd, 'w', encoding='utf8') as f:
            f.write("\n".join(six.text_type(i) for i in footages))
        for i in progress(list(Path(input_dir).glob("**/*.nk")), "转换Nuke文件为序列工程"):
            proc = subprocess.Popen(
                [nuke.EXE_PATH,
                 '-t',
                 __main__.__file__,
                 '--input', str(i),
                 '--output', str(Path(output_dir) / i.name),
                 '--footage-list', temp_fp,
                 ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate()
            nuke.tprint(stdout)
            nuke.tprint(stderr)
            assert proc.wait() == 0, proc.returncode
        webbrowser.open(output_dir)
    finally:
        try:
            os.unlink(temp_fp)
        except OSError:
            pass
