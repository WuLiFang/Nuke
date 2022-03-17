# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import absolute_import, division, print_function, unicode_literals

import contextlib
import logging

from wulifang.vendor import six
from wulifang.vendor.Qt import QtGui
from wulifang.vendor.Qt.QtWidgets import QAction, QMenu

import hiero.core.events
import hiero.ui
import hiero.core

from .. import codectools
from . import message, track_item

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Callable, Iterator, List, Text, Optional

    EventCallback = Callable[[hiero.core.events.Event], None]


_LOGGER = logging.getLogger(__name__)

_MENU_TITLE = "吾立方"
_OBJECT_NAME_PREFIX = __name__ + "."
_MENU_OBJECT_NAME = _OBJECT_NAME_PREFIX + "menu"
_CLEANUP_KEY = "_WULIFANG_GUI_CLEANUPS"


class _g:
    actions = []  # type: List[QAction]
    setups = []  # type: List[Callable[[], None]]


def _cleanups():
    # type: () -> List[Callable[[],None]]
    cleanups = getattr(hiero.ui, _CLEANUP_KEY, None)
    if cleanups is None:
        setattr(hiero.ui, _CLEANUP_KEY, [])
        return _cleanups()
    return cleanups


@contextlib.contextmanager
def _exception_as_message():
    try:
        yield
    except Exception as ex:
        message.error(codectools.text(six.text_type(ex)))


@contextlib.contextmanager
def _undo_group(project, name):
    # type: (Optional[hiero.core.Project], Text) -> Iterator[None]
    if project:
        with project.beginUndo(name):
            yield
    else:
        yield


def _on_event(t):
    # type: (Text) -> Callable[[EventCallback],EventCallback]

    def _wrapper(cb):
        # type: (EventCallback) -> EventCallback
        def _setup():
            hiero.core.events.registerInterest(t, cb)

            def _cleanup():
                hiero.core.events.unregisterInterest(t, cb)

            _cleanups().append(_cleanup)

        _g.setups.append(_setup)

        return cb

    return _wrapper


def _actions():
    # type: () -> Iterator[QAction]

    def _action1():
        a = QAction("以所选对齐其他轨道")
        a.setObjectName(_OBJECT_NAME_PREFIX + "timeline.alignOtherTrackBySelected")
        a.setEnabled(track_item.has_selection())

        def _align_other_track_by_selected():
            with _exception_as_message():
                ap = track_item.align_other_track_by(track_item.selection())
                message.info(ap.explain())

        a.triggered.connect(_align_other_track_by_selected)

        @_on_event("kSelectionChanged")
        def _(event):
            # type: (hiero.core.events.Event,) -> None
            a.setEnabled(track_item.has_selection())

        return a

    yield _action1()

    def _action3():
        a = QAction("移除所选名称中的版本后缀")
        a.setObjectName(_OBJECT_NAME_PREFIX + "timeline.removeVersionSuffix")
        a.setEnabled(track_item.has_selection())

        def _receiver():
            with _exception_as_message():
                for project, items in track_item.group_by_project(
                    track_item.selection()
                ):
                    with _undo_group(project, a.text()):
                        res = track_item.remove_version_suffix(iter(items))
                        message.info("重命名了 %d 项" % len(res))

        a.triggered.connect(_receiver)

        @_on_event("kSelectionChanged")
        def _(event):
            # type: (hiero.core.events.Event,) -> None
            a.setEnabled(track_item.has_selection())

        return a

    yield _action3()

    def _action2():
        a = QAction("重新加载吾立方插件")
        a.setObjectName(_OBJECT_NAME_PREFIX + "reload")
        a.setShortcut(QtGui.QKeySequence("Ctrl+Shift+F5"))

        def _reload():
            with _exception_as_message():
                from ._init import reload

                _LOGGER.info("reload")
                reload()

        a.triggered.connect(_reload)
        return a

    yield _action2()


@_on_event("kShowContextMenu/kTimeline")
def _(event):
    # type: (hiero.core.events.Event,) -> None
    m = event.menu
    for i in m.actions():
        if i.objectName().startswith(_OBJECT_NAME_PREFIX):
            m.removeAction(i)

    for i in _g.actions:
        if i.objectName().startswith(_OBJECT_NAME_PREFIX + "timeline."):
            _ = m.addAction(i)


def init_gui():
    cleanups = _cleanups()
    while cleanups:
        with _exception_as_message():
            cleanups.pop()()

    _g.actions = list(_actions())
    bar = hiero.ui.menuBar()
    m = bar.findChild(QMenu, _MENU_OBJECT_NAME) or bar.addMenu(_MENU_TITLE)
    m.setObjectName(_MENU_OBJECT_NAME)
    m.clear()

    for i in _g.actions:
        _ = m.addAction(i)

    for i in _g.setups:
        i()
