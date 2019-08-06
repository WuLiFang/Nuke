# -*- coding=UTF-8 -*-
"""Asset notify.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import functools
import io
import logging
import os
import time
import webbrowser
from tempfile import mkstemp

import nuke
import pendulum
from jinja2 import Environment, FileSystemLoader

import callback
from executor import EXECUTOR
from nuketools import utf8
from wlf.codectools import get_encoded as e
from wlf.codectools import get_unicode as u
from wlf.decorators import run_with_clock

from . import core
from .monitor import FootagesMonitor

LOGGER = logging.getLogger(__name__)


def warn_missing_frames(assets=None, show_ok=False):
    """Show missing frames to user
        Args:
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

SHOWED_WARNING = []


def throtted_warning(msg):
    """Only show each warning message once.  """

    msg = u(msg)
    if msg not in SHOWED_WARNING:
        nuke.warning(utf8(msg))
        SHOWED_WARNING.append(msg)


def reset_warning_history():
    """Forget showed warning.  """

    del SHOWED_WARNING[:]


def warn_mtime(show_ok=False, since=None):
    """Show footage that mtime newer than script mtime. """

    LOGGER.debug('Check warn_mtime')

    try:
        script_name = nuke.scriptName()
    except RuntimeError:
        if show_ok:
            nuke.message(utf8('文件未保存'))
        return
    script_mtime = os.path.getmtime(e(script_name))
    since = since or script_mtime

    @run_with_clock('检查素材修改日期')
    def _get_mtime_info():
        ret = {}
        for n in nuke.allNodes('Read', nuke.Root()):
            try:
                mtime = time.mktime(time.strptime(
                    n.metadata('input/mtime'), '%Y-%m-%d %H:%M:%S'))
            except TypeError:
                continue
            if mtime > since:
                ret[nuke.filename(n)] = mtime
                ftime = time.strftime('%m-%d %H:%M:%S', time.localtime(mtime))
                throtted_warning(
                    '{}: [new footage]{}'.format(u(n.name()), ftime))
        return ret

    newer_footages = _get_mtime_info()

    if not (show_ok or newer_footages):
        return

    env = Environment(loader=FileSystemLoader(core.TEMPLATES_DIR))
    template = env.get_template('mtime.html')
    data = [(k, pendulum.from_timestamp(v).diff_for_humans())
            for k, v in newer_footages.items()]
    msg = template.render(script_name=script_name,
                          script_mtime=pendulum.from_timestamp(
                              script_mtime).diff_for_humans(),
                          data=data)
    nuke.message(utf8(msg))

def setup():
    pendulum.set_locale('zh')
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(reset_warning_history)
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(warn_missing_frames)
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(warn_mtime)
    callback.CALLBACKS_ON_SCRIPT_SAVE.append(warn_missing_frames)
