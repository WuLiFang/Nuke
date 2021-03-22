# -*- coding=UTF-8 -*-
"""custom progress handlers.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from wlf.progress.handlers.nuke import NukeProgressHandler


class CustomMessageProgressHandler(NukeProgressHandler):
    """Progress message from object.  """

    def __init__(self, message_factory, **kwargs):
        super(CustomMessageProgressHandler, self).__init__(**kwargs) # type: ignore
        self._message_factory = message_factory

    def message_factory(self, item):
        return self._message_factory(item)


class NodeProgressHandler(NukeProgressHandler):
    """Progress message from node name.  """

    def message_factory(self, item):
        return item.name() # type: ignore
