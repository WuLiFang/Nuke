# -*- coding=UTF-8 -*-
"""Nuke tools for programing.  """
from __future__ import absolute_import, unicode_literals

import logging
import threading
from contextlib import contextmanager
from functools import wraps

import nuke

from wlf.codectools import get_encoded
from wlf.decorators import run_in_main_thread

LOGGER = logging.getLogger('com.wlf.nuketools')

# TODO: replace utf8 related code with cast_unknown

class UTF8Object(object):
    """UTF8Wraper for nuke object.  """

    def __new__(cls, obj):
        if obj is None or isinstance(obj, (float, int, UTF8Object)):
            return obj
        return super(UTF8Object, cls).__new__(cls, obj)

    def __init__(self, obj):
        if obj is self:
            return
        self.obj = obj
        for i in dir(obj):
            if not i.startswith('_') and i in self.__dict__:
                continue
            try:
                self.__dict__[i] = utf8(getattr(obj, i))
            except AttributeError:
                self.__dict__[i] = getattr(obj, i)

    def __repr__(self):
        return get_encoded('|utf8 {}|' .format(repr(self.obj).decode('utf-8')))

    def __dir__(self):
        return dir(self.obj)

    def __getitem__(self, name):
        return utf8(self.obj.__getitem__(name))


def utf8(obj):
    """Convert unicode to str with utf8 encoding.  """

    if isinstance(obj, (str, unicode)):
        return get_encoded(obj, 'utf-8')
    elif isinstance(obj, dict):
        return utf8_dict(obj)

    return obj


def iutf8(iterable):
    """Convert unicode to utf8 string for @iterable.  """

    for i in iterable:
        yield utf8(i)


def utf8_dict(dict_):
    """Return new dict with @dict_ keys has been
    converted from unicode to utf8 string.
    """
    assert isinstance(dict_, dict)

    ret = dict(dict_)
    for i in ret:
        ret[i] = utf8(ret[i])
    return ret


def utf8_func(func):
    """(Decorator)Wrap utf8 only @func to support unicode.  """

    @wraps(func)
    def _func(*args, **kwargs):
        args = tuple(utf8(i) for i in args)
        kwargs = utf8_dict(kwargs)
        try:
            ret = func(*args, **kwargs)
        except:
            nuke.message(repr(func))
            raise
        if isinstance(ret, str):
            ret = ret.decode('utf-8')
        elif callable(ret):
            ret = UTF8Object(ret)
        return ret

    return _func


def undoable_func(name=None):
    """(Decorator)Record nuke undo set for @func.   """

    def _wrap(func):

        @wraps(func)
        def _func(*args, **kwargs):
            _name = name if name is not None else func.__name__
            run_in_main_thread(nuke.Undo.begin)(utf8(_name))

            try:
                ret = func(*args, **kwargs)
                if not isinstance(ret, threading.Thread):
                    # Async function should call nuke.Undo.end by itself.
                    run_in_main_thread(nuke.Undo.end)()
                else:
                    LOGGER.warning(
                        'Async function should implement undoable itself.')
                return ret
            except:
                run_in_main_thread(nuke.Undo.cancel)()
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
    """Restore modifield status after action finished.
    """

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
