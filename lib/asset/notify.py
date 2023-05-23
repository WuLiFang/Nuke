# -*- coding=UTF-8 -*-
"""Asset notify.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import io
import logging
import os
import time
import webbrowser
from tempfile import mkstemp

import nuke
import pendulum
from jinja2 import Environment, FileSystemLoader

import wulifang
import callback
import cast_unknown as cast
import templates
from wlf.decorators import run_with_clock

from . import core

LOGGER = logging.getLogger(__name__)


def warn_missing_frames(nodes=None, show_ok=False):
    """Show missing frames to user
    Args:
        assets (any, optional): Defaults to None.
        object contains assets, None mean all Assets.
        show_ok (bool, optional): Defaults to False.
        If show message for no missing frames.
    """
    if nodes is None:
        nodes = nuke.allNodes(b"Read")

    result = []
    for n in nodes:
        filename = cast.text(nuke.filename(n))
        frame_ranges = list(
            wulifang.file.missing_frames(filename, n.firstFrame(), n.lastFrame())
        )
        if not frame_ranges:
            continue
        result.append(
            dict(
                nodename=cast.text(n.name()),
                filename=filename,
                frame_ranges=nuke.FrameRanges(frame_ranges),
            )
        )

    html = templates.render(
        "missing_frames.tmpl",
        dict(
            result=result,
        ),
    )

    if not result:
        if show_ok:
            nuke.message(cast.binary("没有发现缺帧素材"))
        return

    if not nuke.GUI:
        LOGGER.warning(result)
        return

    if len(result) < 10:
        nuke.message(cast.binary(html.replace("\n", "")))
    else:
        fd, _ = mkstemp(".html", text=True)
        with io.open(fd, "w", encoding="utf-8") as f:
            _ = f.write(html)
        _ = webbrowser.open(html)


SHOWED_WARNING = []


def throtted_warning(msg):
    """Only show each warning message once."""

    msg = cast.text(msg)
    if msg not in SHOWED_WARNING:
        nuke.warning(cast.binary(msg))
        SHOWED_WARNING.append(msg)


def reset_warning_history():
    """Forget showed warning."""

    del SHOWED_WARNING[:]


def warn_mtime(show_ok=False, since=None):
    """Show footage that mtime newer than script mtime."""

    LOGGER.debug("Check warn_mtime")

    try:
        script_name = nuke.scriptName()
    except RuntimeError:
        if show_ok:
            nuke.message(cast.binary("文件未保存"))
        return
    script_mtime = os.path.getmtime(cast.binary(script_name))
    since = since or script_mtime

    @run_with_clock("检查素材修改日期")
    def _get_mtime_info():
        ret = {}
        for n in nuke.allNodes(b"Read", nuke.Root()):
            mtime_text = n.metadata(b"input/mtime")
            if mtime_text is None:
                continue
            mtime = time.mktime(
                time.strptime(
                    cast.text(mtime_text),
                    "%Y-%m-%d %H:%M:%S",
                )
            )
            if mtime > since:
                ret[nuke.filename(n)] = mtime
                ftime = time.strftime("%m-%d %H:%M:%S", time.localtime(mtime))
                throtted_warning(
                    "{}: [new footage]{}".format(cast.text(n.name()), ftime)
                )
        return ret

    newer_footages = _get_mtime_info()

    if not (show_ok or newer_footages):
        return

    env = Environment(loader=FileSystemLoader(core.TEMPLATES_DIR))
    template = env.get_template("mtime.html")
    data = [
        (k, pendulum.from_timestamp(v).diff_for_humans())
        for k, v in newer_footages.items()
    ]
    msg = template.render(
        script_name=script_name,
        script_mtime=pendulum.from_timestamp(script_mtime).diff_for_humans(),
        data=data,
    )
    nuke.message(cast.binary(msg))


def setup():
    pendulum.set_locale("zh")
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(reset_warning_history)
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(warn_mtime)
