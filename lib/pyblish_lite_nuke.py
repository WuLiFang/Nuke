# -*- # -*- coding=UTF-8 -*-
"""Pyblish lite nuke interagation.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import multiprocessing
import multiprocessing.dummy
import os
import Queue

import nuke
import pyblish.plugin
import six
from nukescripts.panels import restorePanel
from Qt import QtGui
from Qt.QtCore import Qt, QObject
from Qt.QtWidgets import QApplication

import callback
import filetools
import nuketools
import panels
import pyblish_asset
import pyblish_cgtwn
import pyblish_lite
import pyblish_lite.delegate
from nuketools import abort_modified, mainwindow
from pyblish_lite import app, control, settings, util, window
import cast_unknown as cast
import wulifang

ACTION_QUEUE = multiprocessing.dummy.Queue()
ACTION_LOCK = multiprocessing.Lock()
LOGGER = logging.getLogger(__name__)


def _do_actions():
    with ACTION_LOCK:
        while True:
            try:
                args = ACTION_QUEUE.get(block=False)
            except Queue.Empty:
                break

            try:
                _pyblish_action(*args)
            except RuntimeError:
                pass


def _after_signal(signal, func):
    def _func():
        signal.disconnect(_func)
        func()

    signal.connect(_func)


def pyblish_action(name, is_block=True, is_reset=False):
    """Control pyblish."""

    if Window.instance and Window.instance.controller.is_running:
        return

    if ACTION_LOCK.acquire(block=is_block):
        ACTION_LOCK.release()
    elif not is_block:
        return

    ACTION_QUEUE.put((name, is_reset))
    _do_actions()


def _pyblish_action(name, is_reset=True):

    if nuke.value(b"root.name", None):
        Window.dock()

    window_ = Window.instance
    if not window_:
        # closed
        return
    assert isinstance(window_, Window)
    controller = window_.controller
    assert isinstance(controller, control.Controller)

    start = getattr(window_, name)
    signal = {
        "publish": controller.was_published,
        "validate": controller.was_validated,
    }[name]

    finish_event = multiprocessing.Event()
    _after_signal(signal, finish_event.set)

    if is_reset:
        # Run after reset finish.
        _after_signal(controller.was_reset, start)
        window_.reset()
    else:
        # Run directly.
        start()

    # Wait finish.
    while not finish_event.is_set() or controller.is_running:
        QApplication.processEvents()


def _handle_result(result):
    def _get_text():
        records = result["records"]
        if records:
            return "\n".join(i.getMessage() for i in records)

        return "请在pyblish窗口中查看详情"

    if not result["success"]:
        wulifang.message.error(_get_text(), title="发布失败")


class _SingletonMeta(type(QObject)):
    _instance = None

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            instance = QObject.__new__(QObject, "", (), {})
            instance.__init__(*args, **kwargs)
            self._instance = instance
        return self._instance


@six.with_metaclass(_SingletonMeta)
class Window(window.Window):
    """Modified pyblish_lite window for nuke.

    Args:
        parent (QtCore.QObject): Qt parent.

    Raises:
        ValueError: When already exists another pyblish window.
    """

    _is_initiated = False
    instance = None

    def __init__(self, parent=None):
        if self._is_initiated:
            return

        controller = control.Controller()
        controller.was_processed.connect(_handle_result)
        super(Window, self).__init__(controller, parent)

        self.resize(*settings.WindowSize)
        self.setWindowTitle(settings.WindowTitle)

        with open(cast.binary(filetools.module_path("pyblish_lite.css"))) as f:
            css = cast.text(f.read())

            # Make relative paths absolute
            root = util.get_asset("").replace("\\", "/")
            css = css.replace('url("', 'url("%s' % root)
        self.setStyleSheet(css.encode("utf-8"))

        self.setObjectName("PyblishWindow")
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self._is_initiated = True

        def _unset():
            Window.instance = None

        self.destroyed.connect(_unset)

    def activate(self):
        """Active pyblish window."""

        LOGGER.debug("activate pyblish window: is_panel=%s", not self.isWindow())
        if self.isWindow():
            self.showNormal()
        else:
            nuketools.raise_panel("com.wlf.pyblish")

    @classmethod
    def dock(cls):
        """Dock pyblish panel in same pane of properties,
        or pop it out.
        """

        try:
            window_ = cls.instance
            if not cls.instance:
                pane = nuke.getPaneFor(b"Properties.1")
                if pane:
                    panel = restorePanel(b"com.wlf.pyblish")
                    panel.addToPane(pane)
                else:
                    _ = Window(mainwindow() or QApplication.activeWindow())
            try:
                cls.instance.activate()
            except RuntimeError:
                cls.instance = None
                cls.dock()
        except:
            LOGGER.exception("dock failed")
            raise

    def get_parent(self, parent_class):
        """Get parent for window.

        Args:
            parent_class (class): Parent class

        Raises:
            ValueError: No such parent.

        Returns:
            parent_class: First matched parent.
        """

        parent = self
        while parent:
            parent = parent.parent()
            if isinstance(parent, parent_class):
                return parent
        raise ValueError("No such parent")


def set_preferred_fonts(font, scale_factor=None):
    """Set preferred font."""

    if scale_factor:
        pyblish_lite.delegate.scale_factor = scale_factor
    else:
        scale_factor = pyblish_lite.delegate.scale_factor
    pyblish_lite.delegate.fonts.update(
        {
            "h3": QtGui.QFont(font, 10 * scale_factor, 900),
            "h4": QtGui.QFont(font, 8 * scale_factor, 400),
            "h5": QtGui.QFont(font, 8 * scale_factor, 800),
        }
    )


def setup():
    panels.register(Window, cast.binary("发布"), b"com.wlf.pyblish")

    callback.CALLBACKS_ON_SCRIPT_LOAD.append(
        lambda: pyblish_action("validate", is_block=True, is_reset=True)
    )
    callback.CALLBACKS_ON_SCRIPT_SAVE.append(
        lambda: pyblish_action("validate", is_block=False, is_reset=True)
    )
    callback.CALLBACKS_ON_SCRIPT_CLOSE.append(
        abort_modified(lambda: pyblish_action("publish", is_block=True, is_reset=False))
    )

    # Remove default plugins.
    pyblish.plugin.deregister_all_paths()
    if os.getenv("DEBUG") != "pyblish":
        settings.TerminalLoglevel = logging.INFO

    app.install_fonts()
    app.install_translator(QApplication.instance())
    set_preferred_fonts("微软雅黑", 1.2)

    for mod in (pyblish_cgtwn, pyblish_asset):
        for i in pyblish.plugin.plugins_from_module(mod):
            pyblish.plugin.register_plugin(i)
