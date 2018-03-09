# -*- # -*- coding=UTF-8 -*-
"""Pyblish lite nuke interagation.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from threading import Event

import nuke
import pyblish.plugin
from nukescripts.panels import restorePanel  # pylint: disable=import-error
from pyblish_lite import app, control, settings, util, window
from Qt.QtWidgets import QApplication, QDialog, QStackedWidget, QMainWindow

import callback
import panels
import pyblish_asset
import pyblish_cgtwn
from nuketools import abort_modified, mainwindow


def _pyblish_action(name, block=False):
    def _func(cls):
        cls.dock()
        window_ = cls.window
        assert isinstance(window_, Window)
        controller = window_.controller
        assert isinstance(controller, control.Controller)
        controller.warning = window_.warning

        finish_event = Event()
        signal = {'publish': controller.was_published,
                  'validate': controller.was_validated}[name]

        def _action():
            assert isinstance(controller, control.Controller)
            controller.was_reset.disconnect(_action)
            if block:
                signal.connect(finish_event.set)
            getattr(window_, name)()

        controller.was_reset.connect(_action)
        window_.reset()
        if block:
            while not finish_event.is_set():
                QApplication.processEvents()
            signal.disconnect(finish_event.set)

    _func.__name__ = name.encode('utf-8', 'replace')
    return classmethod(_func)


class Pyblish(object):
    """Pyblish manager for nuke.   """

    window = None

    @classmethod
    def dock(cls):
        """Dock pyblish panel in same pane of properties,
            or pop it out.
        """

        window_ = cls.window
        if not window_:
            pane = nuke.getPaneFor('Properties.1')
            if pane:
                panel = restorePanel('com.wlf.pyblish')
                panel.addToPane(pane)
            else:
                try:
                    window_ = Window(mainwindow())
                except RuntimeError:
                    window_ = Window()
                window_.show()
        else:
            try:
                window_.activate()
            except ValueError:
                # Window already closed.
                cls.window = None
                window_.close()
                window_.deleteLater()
                cls.dock()
            except RuntimeError:
                # Window already deleted.
                cls.window = None
                cls.dock()

    publish = _pyblish_action('publish', True)
    validate = _pyblish_action('validate')


class Window(window.Window):
    """Modified pyblish_lite window for nuke.

    Args:
        parent (QtCore.QObject): Qt parent.

    Raises:
        ValueError: When already exists another pyblish window.
    """

    def __init__(self, parent=None):
        if Pyblish.window:
            raise ValueError('Single instance.')
        Pyblish.window = self

        super(Window, self).__init__(
            control.Controller(), parent)

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

    def closeEvent(self, event):
        super(Window, self).closeEvent(event)
        Pyblish.window = None

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


def setup():
    """Set up pyblish.   """

    panels.register(Window, 'Pyblish', 'com.wlf.pyblish')

    callback.CALLBACKS_ON_SCRIPT_LOAD.append(Pyblish.validate)
    callback.CALLBACKS_ON_SCRIPT_SAVE.append(Pyblish.validate)
    callback.CALLBACKS_ON_SCRIPT_CLOSE.append(abort_modified(Pyblish.publish))

    # Remove default plugins.
    pyblish.plugin.deregister_all_paths()

    app.install_fonts()
    app.install_translator(QApplication.instance())

    for mod in (pyblish_cgtwn, pyblish_asset):
        for i in pyblish.plugin.plugins_from_module(mod):
            pyblish.plugin.register_plugin(i)
