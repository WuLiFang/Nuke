# -*- # -*- coding=UTF-8 -*-
"""Pyblish lite nuke interagation.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
from threading import Event

import nuke
import pyblish.plugin
from nukescripts.panels import restorePanel  # pylint: disable=import-error
from pyblish_lite import app, control, settings, util, window
from Qt.QtCore import Qt
from Qt.QtWidgets import QApplication, QDialog, QMainWindow, QStackedWidget

import callback
import panels
import pyblish_asset
import pyblish_cgtwn
from nuketools import abort_modified, mainwindow


def _pyblish_action(name, is_block=False, is_reset=True):
    def _func():
        if nuke.value('root.name', None):
            Window.dock()
        window_ = Window.instance
        assert isinstance(window_, Window)
        controller = window_.controller
        assert isinstance(controller, control.Controller)

        finish_event = Event()
        signal = {'publish': controller.was_published,
                  'validate': controller.was_validated}[name]

        def _action():
            assert isinstance(controller, control.Controller)
            controller.was_reset.disconnect(_action)
            _start()

        def _start():
            if is_block:
                signal.connect(finish_event.set)
            getattr(window_, name)()

        # Wait finish previous running.
        while window_.is_running:
            QApplication.processEvents()

        if is_reset:
            # Run after reset finish.
            controller.was_reset.connect(_action)
            window_.reset()
        else:
            # Run directly.
            _start()

        if is_block:
            # Wait finish.
            while not finish_event.is_set():
                QApplication.processEvents()
            signal.disconnect(finish_event.set)
            error = controller.current_error
            if error:
                raise callback.AbortedError(error)

    _func.__name__ = name.encode('utf-8', 'replace')
    return _func


class Window(window.Window):
    """Modified pyblish_lite window for nuke.

    Args:
        parent (QtCore.QObject): Qt parent.

    Raises:
        ValueError: When already exists another pyblish window.
    """
    is_running = False
    _is_initiated = False
    instance = None
    controller = control.Controller()

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

        font = self.font()
        font.setFamily("Open Sans")
        font.setPointSize(8)
        font.setWeight(400)

        self.setFont(font)

        with open(util.get_asset("app.css")) as f:
            css = f.read()

            # Make relative paths absolute
            root = util.get_asset("").replace("\\", "/")
            css = css.replace("url(\"", "url(\"%s" % root)
        self.setStyleSheet(css)

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

    def validate(self):
        if self.is_running:
            return
        self.is_running = True
        super(Window, self).validate()

    def publish(self):
        if self.is_running:
            return
        self.is_running = True

        super(Window, self).publish()

    def on_finished(self):
        self.is_running = False

        super(Window, self).on_finished()


def setup():
    panels.register(Window, '发布', 'com.wlf.pyblish')

    callback.CALLBACKS_ON_SCRIPT_LOAD.append(
        _pyblish_action('validate'))
    callback.CALLBACKS_ON_SCRIPT_SAVE.append(
        _pyblish_action('validate'))
    callback.CALLBACKS_ON_SCRIPT_CLOSE.append(
        abort_modified(_pyblish_action('publish', True, False)))

    # Remove default plugins.
    pyblish.plugin.deregister_all_paths()
    try:
        settings.TerminalLoglevel = int(os.getenv('LOGLEVEL'))
    except TypeError:
        settings.TerminalLoglevel = 20

    app.install_fonts()
    app.install_translator(QApplication.instance())

    for mod in (pyblish_cgtwn, pyblish_asset):
        for i in pyblish.plugin.plugins_from_module(mod):
            pyblish.plugin.register_plugin(i)
