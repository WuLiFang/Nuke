# -*- coding=UTF-8 -*-
"""Asset notify.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import io
import logging
import os
import time
import webbrowser
from tempfile import mkstemp

import nuke

from node import Last
from nuketools import utf8
from wlf.decorators import run_with_clock

from .monitor import FootagesMonitor

LOGGER = logging.getLogger(__name__)


def warn_missing_frames(assets=None, show_ok=False):
    """Show missing frames to user
        assets (any, optional): Defaults to None.
            object contains assets, None mean all Assets.
        show_ok (bool, optional): Defaults to False.
            If show message for no missing frames.
    """

    if assets is None:
        assets = FootagesMonitor.all()
    else:
        assets = FootagesMonitor(assets)

    result = assets.missing_frames_dict()
    if not result:
        if show_ok:
            nuke.message(utf8('没有发现缺帧素材'))
    elif len(result) < 10:
        if nuke.GUI:
            nuke.message(utf8(result.as_html().replace('\n', '')))
        else:
            LOGGER.warning(result)
    else:
        # Use html to display.
        fd, name = mkstemp('.html', text=True)
        with io.open(fd, 'w') as f:
            f.write(result.as_html())
        webbrowser.open(name)


def warn_mtime(show_dialog=False, show_ok=False):
    """Show footage that mtime newer than script mtime. """

    LOGGER.debug('Check warn_mtime')
    msg = ''
    newer_footages = {}

    @run_with_clock('检查素材修改日期')
    def _get_mtime_info():
        for n in nuke.allNodes('Read', nuke.Root()):
            try:
                mtime = time.strptime(n.metadata(
                    'input/mtime'), '%Y-%m-%d %H:%M:%S')
            except TypeError:
                continue
            if mtime > Last.mtime:
                ftime = time.strftime('%m-%d %H:%M:%S', mtime)
                newer_footages[nuke.filename(n)] = ftime
                msg = '{}: [new footage]{}'.format(n.name(), ftime)
                if msg not in Last.showed_warning:
                    nuke.warning(msg)
                    Last.showed_warning.append(msg)

    _get_mtime_info()

    if show_dialog and (newer_footages or show_ok):
        msg = '<style>td {padding:8px;}</style>'
        msg += '<b>{}</b>'.format((os.path.basename(Last.name)))
        msg += '<div>上次修改: {}</div><br><br>'.format(
            time.strftime('%y-%m-%d %H:%M:%S', Last.mtime))
        if newer_footages:
            msg += '发现以下素材变更:<br>'
            msg += '<tabel>'
            msg += '<tr><th>修改日期</th><th>素材</th></tr>'
            msg += '\n'.join(['<tr><td>{}</td><td>{}</td></tr>'.format(
                newer_footages[i], i)
                for i in newer_footages])
            msg += '</tabel>'
        elif show_ok:
            msg += '没有发现更新的素材'
        nuke.message(utf8(msg))
