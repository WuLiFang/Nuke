# -*- # -*- coding=UTF-8 -*-
"""Pyblish lite nuke interagation.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import os
from multiprocessing.dummy import Event, Lock, Queue

import nuke
import pyblish.plugin
import pyblish_lite
from nukescripts.panels import restorePanel  # pylint: disable=import-error
from pyblish_lite import app, control, settings, util, window
from Qt import QtGui
from Qt.QtCore import Qt
from Qt.QtWidgets import QApplication, QDialog, QMainWindow, QStackedWidget

import callback
import filetools
import panels
import pyblish_asset
import pyblish_cgtwn
from nuketools import abort_modified, mainwindow
from wlf.codectools import get_encoded as e
from wlf.codectools import get_unicode as u

ACTION_QUEUE = Queue()
ACTION_LOCK = Lock()


def _do_actions():
    with ACTION_LOCK:
        while not ACTION_QUEUE.empty():
            try:
                ACTION_QUEUE.get()()
            except RuntimeError:
                pass


def _after_signal(signal, func):
    def _func():
        signal.disconnect(_func)
        func()
    signal.connect(_func)


def _validate():
    ACTION_QUEUE.put(_pyblish_action('validate', True))
    _do_actions()


def _publish():
    ACTION_QUEUE.put(_pyblish_action('publish', False))
    _do_actions()


def _pyblish_action(name, is_reset=True):
    def _func():
        if nuke.value('root.name', None):
            Window.dock()

        window_ = Window.instance
        assert isinstance(window_, Window)
        controller = window_.controller
        assert isinstance(controller, control.Controller)

        start = getattr(window_, name)
        signal = {'publish': controller.was_published,
                  'validate': controller.was_validated}[name]

        finish_event = Event()
        _after_signal(signal, finish_event.set)

        if is_reset:
            # Run after reset finish.
            _after_signal(controller.was_reset, start)
            window_.reset()
        else:
            # Run directly.
            start()

        # Wait finish.
        while (not finish_event.is_set()
               or controller.is_running):
            QApplication.processEvents()

    _func.__name__ = name.encode('utf-8', 'replace')
    return _func


class Window(window.Window):
    """Modified pyblish_lite window for nuke.

    Args:
        parent (QtCore.QObject): Qt parent.

    Raises:
        ValueError: When already exists another pyblish window.
    """

    _is_initiated = False
    instance = None

    def __new__(cls, parent=None):
        if not cls.instance:
            cls.instance = super(Window, cls).__new__(cls, parent)
        return cls.instance

    def __init__(self, parent=None):
        if self._is_initiated:
            return

        controller = control.Controller()
        super(Window, self).__init__(
            controller, parent)

        self.resize(*settings.WindowSize)
        self.setWindowTitle(settings.WindowTitle)

        with open(e(filetools.path("pyblish_lite.css"))) as f:
            css = u(f.read())

            # Make relative paths absolute
            root = util.get_asset("").replace("\\", "/")
            css = css.replace("url(\"", "url(\"%s" % root)
        self.setStyleSheet(css.encode('utf-8'))

        self.setObjectName('PyblishWindow')
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self._is_initiated = True

    def activate(self):
        """Active pyblish window.   """

        if isinstance(self.parent(), QMainWindow):
            # Show as a standalone dialog.
            self.raise_()
        else:
            # Show in panel.
            panel = self.get_parent(QStackedWidget)
            dialog = self.get_parent(QDialog)
            panel.setCurrentWidget(dialog)

    @classmethod
    def dock(cls):
        """Dock pyblish panel in same pane of properties,
            or pop it out.
        """

        window_ = cls.instance
        if not window_:
            try:
                mainwindow_ = mainwindow()
                pane = nuke.getPaneFor('Properties.1')
                if pane:
                    panel = restorePanel('com.wlf.pyblish')
                    panel.addToPane(pane)
                else:
                    window_ = Window(mainwindow_)
                    window_.show()
            except RuntimeError:
                window_ = Window()
                window_.show()
        else:
            try:
                window_.activate()
            except ValueError:
                # Window already closed.
                cls.instance = None
                window_.close()
                window_.deleteLater()
                cls.dock()
            except RuntimeError:
                # Window already deleted.
                cls.instance = None
                cls.dock()

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
        raise ValueError('No such parent')


def set_preferred_fonts(font, scale_factor=None):
    """Set preferred font.  """

    if scale_factor:
        pyblish_lite.delegate.scale_factor = scale_factor
    else:
        scale_factor = pyblish_lite.delegate.scale_factor
    pyblish_lite.delegate.fonts.update({
        "h3": QtGui.QFont(font, 10 * scale_factor, 900),
        "h4": QtGui.QFont(font, 8 * scale_factor, 400),
        "h5": QtGui.QFont(font, 8 * scale_factor, 800)})


def setup():
    panels.register(Window, '发布', 'com.wlf.pyblish')

    callback.CALLBACKS_ON_SCRIPT_LOAD.append(_validate)
    callback.CALLBACKS_ON_SCRIPT_SAVE.append(_validate)
    callback.CALLBACKS_ON_SCRIPT_CLOSE.append(abort_modified(_publish))

    # Remove default plugins.
    pyblish.plugin.deregister_all_paths()
    try:
        settings.TerminalLoglevel = int(
            logging.getLevelName(os.getenv('LOGLEVEL')))
    except (TypeError, ValueError):
        settings.TerminalLoglevel = 20

    app.install_fonts()
    app.install_translator(QApplication.instance())
    set_preferred_fonts('微软雅黑', 1.2)

    for mod in (pyblish_cgtwn, pyblish_asset):
        for i in pyblish.plugin.plugins_from_module(mod):
            pyblish.plugin.register_plugin(i)
