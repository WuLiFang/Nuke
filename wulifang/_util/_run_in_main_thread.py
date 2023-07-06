# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Callable, TypeVar, ParamSpec

    T = TypeVar("T")
    P = ParamSpec("P")

from ._has_nuke_app import has_nuke_app
from ._has_qt_app import has_qt_app
from functools import wraps
from threading import current_thread

from wulifang._util import assert_isinstance, assert_not_none
from multiprocessing.dummy import Queue


def run_in_main_thread(f):
    # type: (Callable[P, T]) -> Callable[P, T]
    """(Decorator)Run @func in nuke main_thread."""

    if has_nuke_app():
        import nuke  # pylint: disable=import-error

        @wraps(f)
        def run_in_nuke_main_thread(*args, **kwargs):
            # type: (Any, Any) -> T
            if nuke.GUI and current_thread().name != "MainThread":
                return nuke.executeInMainThreadWithResult(f, args, kwargs)

            return f(*args, **kwargs)  # type: ignore

        return run_in_nuke_main_thread  # type: ignore

    elif has_qt_app():
        from wulifang.vendor.Qt.QtCore import QObject, QEvent, QCoreApplication
        from wulifang.vendor import Qt

        class Event(QEvent):
            if Qt.IsPySide or Qt.IsPySide2:  # type: ignore
                event_type = QEvent.User
            else:
                event_type = QEvent.registerEventType()

            def __init__(self, func, args, kwargs):
                # type: (Callable[P,T], Any, Any) -> None
                super(Event, self).__init__(self.event_type)
                self.func = func
                self.args = args
                self.kwargs = kwargs

            def run(self):
                # type: () -> T
                return self.func(*self.args, **self.kwargs)  # type: ignore

        class Runner(QObject):
            """Runner for run in main thread."""

            result = Queue(1)  # type: Queue[T]

            def event(self, event):
                # type: (QEvent) -> bool
                if isinstance(event, Event):
                    try:
                        self.result.put(assert_isinstance(event, Event).run())
                        return True
                    except AttributeError:
                        return False
                return super(Runner, self).event(event)

        @wraps(f)
        def run_in_qt_main_thread(*args, **kwargs):
            # type: (Any, Any) -> T
            app = assert_not_none(QCoreApplication.instance())
            runner = Runner()
            try:
                runner.moveToThread(app.thread())
                app.notify(runner, Event(f, args, kwargs))
                return runner.result.get()
            finally:
                runner.deleteLater()

        return run_in_qt_main_thread # type: ignore

    return f
