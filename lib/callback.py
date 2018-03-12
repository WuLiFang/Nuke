# -*- coding: UTF-8 -*-
"""Add callback for wlf plugins."""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os

import nuke

import edit
import orgnize
from node import Last, wlf_write_node
from nuketools import abort_modified, utf8
from wlf import csheet
from wlf.path import get_unicode as u

LOGGER = logging.getLogger('com.wlf.callback')


class AbortedError(Exception):
    """Indicate abort execution.   """
    pass


class Callbacks(list):
    """Failsafe callbacks executor.  """

    def execute(self, *args, **kwargs):
        """Execute callbacks.   """
        ret = None
        try:
            for i in self:
                try:
                    ret = i(*args, **kwargs) or ret
                except AbortedError:
                    raise
                except:
                    import inspect

                    LOGGER.error(
                        'Error during execute callback: %s(%s,%s):'
                        '\nfrom %s',
                        i.__name__,
                        args, kwargs,
                        inspect.getsourcefile(i),
                        exc_info=True)

                    raise RuntimeError
        except RuntimeError:
            pass
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
