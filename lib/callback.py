# -*- coding: UTF-8 -*-
"""Add callback for wlf plugins."""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import contextlib

import nuke


LOGGER = logging.getLogger('com.wlf.callback')


class Callbacks(list):
    """Failsafe callbacks executor.  """
    current = None

    @contextlib.contextmanager
    def set_current(self):
        """Set current object during context.  """

        Callbacks.current = self
        try:
            yield
        finally:
            if Callbacks.current is self:
                Callbacks.current = None

    def execute(self, *args, **kwargs):
        """Execute callbacks.   """

        with self.set_current():
            ret = None
            for i in self:
                try:
                    ret = i(*args, **kwargs) or ret
                except:
                    import inspect
                    LOGGER.error(
                        'Error during execute callback: %s(%s,%s):'
                        '\nfrom %s',
                        i.__name__,
                        args, kwargs,
                        inspect.getsourcefile(i),
                        exc_info=True)

                    continue
        return ret


CALLBACKS_BEFORE_RENDER = Callbacks()
CALLBACKS_ON_CREATE = Callbacks()
CALLBACKS_ON_DROP_DATA = Callbacks()
CALLBACKS_ON_USER_CREATE = Callbacks()
CALLBACKS_ON_SCRIPT_LOAD = Callbacks()
CALLBACKS_ON_SCRIPT_SAVE = Callbacks()
CALLBACKS_ON_SCRIPT_CLOSE = Callbacks()
CALLBACKS_UPDATE_UI = Callbacks()


def clean():
    """Remove error callback.  """

    groups = ('onScriptLoads', 'onScriptSaves', 'onScriptCloses',
              'onDestroys', 'onCreates', 'onUserCreates', 'knobChangeds',
              'updateUIs', 'renderProgresses',
              'beforeBackgroundRenders', 'afterBackgroundRenders',
              'beforeBackgroundFrameRenders', 'afterBackgroundFrameRenders',
              'beforeRenders', 'afterRenders',
              'beforeFrameRenders', 'afterFrameRenders',
              'validateFilenames')
    for group in groups:
        group = getattr(nuke, group, None)
        if not isinstance(group, dict):
            continue
        for callbacks in group.values():
            for callback in callbacks:
                try:
                    str(callback)
                except ValueError:
                    callbacks.remove(callback)


def setup():

    nuke.addBeforeRender(CALLBACKS_BEFORE_RENDER.execute)
    nuke.addOnScriptLoad(CALLBACKS_ON_SCRIPT_LOAD.execute)
    nuke.addOnScriptSave(CALLBACKS_ON_SCRIPT_SAVE.execute)
    nuke.addOnScriptClose(CALLBACKS_ON_SCRIPT_CLOSE.execute)
    nuke.addOnCreate(CALLBACKS_ON_CREATE.execute)
    nuke.addUpdateUI(CALLBACKS_UPDATE_UI.execute)
    if nuke.GUI:
        import nukescripts
        nukescripts.addDropDataCallback(CALLBACKS_ON_DROP_DATA.execute)
