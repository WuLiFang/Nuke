# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional, Callable, Tuple
    from wulifang import types

import logging
import multiprocessing
import os
import threading

import nuke
from nukescripts.panels import restorePanel
from wulifang.vendor.pyblish_lite import app, settings
from wulifang.vendor.Qt.QtCore import Signal
from wulifang.vendor.Qt.QtWidgets import QApplication
from wulifang.vendor.six.moves import queue
import wulifang.vendor.cgtwq as cgtwq
from .. import _panels
from . import plugins
from .panel import Window, set_preferred_fonts


def _after_signal(signal, func):
    # type: (Signal, Callable[[],None])-> None
    def _func():
        signal.disconnect(_func)
        func()

    signal.connect(_func)


class PublishService:
    def __init__(self):
        self._window = None  # type: Optional[Window]
        self._action_queue = queue.Queue()  # type: queue.Queue[Tuple[Text, bool]]
        self._action_lock = multiprocessing.Lock()
        _panels.register(
            Window,
            "发布".encode("utf-8"),
            "com.wlf.pyblish".encode("utf-8"),
        )
        if os.getenv("DEBUG") != "pyblish":
            settings.TerminalLoglevel = logging.INFO

        app.install_fonts()
        app.install_translator(QApplication.instance())  # type: ignore
        set_preferred_fonts("微软雅黑", 1.2)

        plugins.register()
        if cgtwq.DesktopClient().executable():
            plugins.cgteamwork.register()

    def _show_window(self):
        if not self._window:
            if Window.last_instance:
                self._window = Window.last_instance
                self._show_window()
                return

            pane = nuke.getPaneFor(b"Properties.1")
            if pane:
                panel = restorePanel(b"com.wlf.pyblish")
                panel.addToPane(pane)
                assert Window.last_instance, "missing publish window"
                self._window = Window.last_instance
            else:
                self._window = Window()
        try:
            self._window.activate()
        except RuntimeError:
            Window.last_instance = None
            self._window = None
            self._show_window()

    def _pyblish_action(self, name, is_reset=True):
        # type: (Text, bool) -> None
        if nuke.value(b"root.name", None):
            self._show_window()
        win = self._window
        if not win:
            # closed
            return
        controller = win.controller

        start = getattr(win, name)
        signal = {
            "publish": controller.was_published,  # type: ignore
            "validate": controller.was_validated,  # type: ignore
        }[
            name
        ]  # type: Signal

        finish_event = threading.Event()
        _after_signal(signal, finish_event.set)

        if is_reset:
            # Run after reset finish.
            _after_signal(controller.was_reset, start)  # type: ignore
            win.reset()
        else:
            # Run directly.
            start()

        # Wait finish.
        while not finish_event.is_set() or controller.is_running:
            QApplication.processEvents()

    def _run(self):
        with self._action_lock:
            while True:
                try:
                    args = self._action_queue.get(block=False)
                except queue.Empty:
                    break
                try:
                    self._pyblish_action(*args)
                except RuntimeError:
                    pass

    def _put_action(self, name, is_block=True, is_reset=False):
        # type: (Text, bool, bool) -> None
        """Control pyblish."""

        if self._window and self._window.controller.is_running:
            return
        self._show_window()
        if self._action_lock.acquire(block=is_block):
            self._action_lock.release()
        elif not is_block:
            return

        self._action_queue.put((name, is_reset))
        self._run()

    def validate(self):
        self._put_action("validate", True, True)

    def request_validate(self):
        self._put_action("validate", False, True)

    def publish(self):
        self._put_action("publish", True, False)


def _(v):
    # type: (PublishService) -> types.PublishService
    return v
