# -*- coding=UTF-8 -*-
"""Dropdata util.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import pluggy

import callback

from . import core, plugins, spec


def get_plugin_manager():
    """Get dropdata plugin manager."""
    plugin_manager = pluggy.PluginManager(core.PROJECT_NAME)
    plugin_manager.add_hookspecs(spec)
    for module in plugins.ALL:
        _ = plugin_manager.register(module)
    _ = plugin_manager.load_setuptools_entrypoints(core.PROJECT_NAME)
    return plugin_manager


def drop(mime_type, data):
    """Drop data from script."""

    plugin_manager = get_plugin_manager()
    return core.dropdata_handler(mime_type, data, plugin_manager.hook)


def setup():
    plugin_manager = get_plugin_manager()

    def _callback(*args, **kwargs):
        kwargs.setdefault("hook", plugin_manager.hook)
        return core.dropdata_handler(*args, **kwargs)

    callback.CALLBACKS_ON_DROP_DATA.append(_callback)
