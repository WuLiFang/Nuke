# -*- coding=UTF-8 -*-
"""Nuke tools for programing.  """
from __future__ import absolute_import, unicode_literals

import logging
import threading
from contextlib import contextmanager
from functools import wraps

import cast_unknown as cast
import nuke

from wlf.decorators import run_in_main_thread

LOGGER = logging.getLogger("com.wlf.nuketools")


def undoable_func(name=None):
    """(Decorator)Record nuke undo set for @func."""

    def _wrap(func):
        @wraps(func)
        def _func(*args, **kwargs):
            _name = name if name is not None else func.__name__
            _ = run_in_main_thread(nuke.Undo.begin)(cast.binary(_name))

            try:
                ret = func(*args, **kwargs)
                if not isinstance(ret, threading.Thread):
                    # Async function should call nuke.Undo.end by itself.
                    _ = run_in_main_thread(nuke.Undo.end)()
                else:
                    LOGGER.warning("Async function should implement undoable itself.")
                return ret
            except:
                _ = run_in_main_thread(nuke.Undo.cancel)()
                raise

        return _func

    return _wrap


def abort_modified(func):
    """(Decorator)Abort function when project has been modified."""

    @wraps(func)
    def _func(*args, **kwargs):
        if nuke.Root().modified():
            return False
        return func(*args, **kwargs)

    return _func


def mainwindow():
    """Get nuke mainwindow.

    Returns:
        Optional[QtWidgets.QMainWindow]: Nuke main window.
    """

    from Qt import QtWidgets

    for i in QtWidgets.QApplication.topLevelWidgets():
        if isinstance(i, QtWidgets.QMainWindow):
            return i


def raise_panel(name):
    # type: (str,) -> None
    """raise panel by name.

    Args:
        name (str): panel name, (e.g. DopeSheet.1)

    Raises:
        RuntimeError: when panel not found.
    """

    from Qt import QtWidgets

    for i in QtWidgets.QApplication.topLevelWidgets():
        panel = i.findChild(QtWidgets.QWidget, name)
        if not panel:
            continue

        parent = panel.parentWidget()
        if not isinstance(parent, QtWidgets.QStackedWidget):
            continue
        index = parent.indexOf(panel)
        parent = parent.parentWidget()
        if not isinstance(parent, QtWidgets.QWidget):
            continue
        tab = parent.findChild(QtWidgets.QTabBar)
        if not tab:
            continue
        tab.setCurrentIndex(index)
        panel.window().raise_()
        return
    else:
        raise RuntimeError("Not found panel: {}".format(name))


@contextmanager
def keep_modifield_status():
    """Restore modifield status after action finished."""

    root = nuke.Root()
    assert isinstance(root, nuke.Root)
    before = root.modified()
    try:
        yield
    finally:
        root.setModified(before)


def selected_node():
    """nuke.selectedNode with a error message.

    Raises:
        ValueError: when no node selected

    Returns:
        nuke.Node: selected node.
    """
    try:
        return nuke.selectedNode()
    except ValueError as ex:
        nuke.message("请选择节点".encode("utf-8"))
        raise ex
