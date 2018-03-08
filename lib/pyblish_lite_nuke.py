# -*- # -*- coding=UTF-8 -*-
"""Pyblish lite nuke interagation.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke
import pyblish.plugin
from nukescripts.panels import restorePanel  # pylint: disable=import-error
from pyblish_lite import app, control, util, window
from Qt.QtWidgets import QApplication, QDialog, QStackedWidget
from Qt.QtCore import QEvent
import pyblish_cgtwn
from nuketools import abort_modified, mainwindow
from wlf.uitools import patch_pyblish_discover


def _pyblish_action(name):
    # @abort_modified
    def _func(cls):
        cls.dock()
        controller = cls.controller()

        def _action():
            controller.was_finished.disconnect(_action)
            getattr(controller, name)()

        controller.was_finished.connect(_action)
        cls.window.reset()

    _func.__name__ = name.encode('utf-8', 'replace')
    return classmethod(_func)


class Pyblish(object):
    window = None
    _controller = None

    @classmethod
    def dock(cls):
        if not cls.window:
            pane = nuke.getPaneFor('Properties.1')
            if pane:
                panel = restorePanel('com.wlf.pyblish')
                panel.addToPane(pane)
                cls.window = panel.custom_knob.getObject().widget
            else:
                cls.window = Window(mainwindow())
                cls.window.setModal(True)
                cls.window.show()
        else:
            try:
                try:
                    panel = cls.get_parent(QStackedWidget)
                    dialog = cls.get_parent(QDialog)
                    panel.setCurrentWidget(dialog)
                except ValueError:
                    # Previous window closed.
                    cls.window.close()
                    cls.window.deleteLater()
            except RuntimeError:
                # Previous window deleted.
                pass
            cls.window = None
            cls.dock()

    @classmethod
    def get_parent(cls, parent_class):
        parent = cls.window
        while parent:
            parent = parent.parent()
            if isinstance(parent, parent_class):
                return parent
        raise ValueError('No such parent')

    @classmethod
    def controller(cls):
        if not cls._controller:
            cls._controller = control.Controller()
        return cls._controller

    publish = _pyblish_action('publish')
    validate = _pyblish_action('validate')


class Window(window.Window):

    def __init__(self, parent=None):
        super(Window, self).__init__(
            Pyblish.controller(), parent)

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

        self.reset()

        Pyblish.window = self
        self.setObjectName('PyblishWindow')


def setup():
    patch_pyblish_discover()

    app.install_fonts()
    app.install_translator(QApplication.instance())

    for i in pyblish.plugin.plugins_from_module(pyblish_cgtwn):
        pyblish.plugin.register_plugin(i)
