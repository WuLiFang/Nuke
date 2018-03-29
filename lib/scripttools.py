# -*- coding=UTF-8 -*-
"""Tools for nuke comp scripts.  """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import contextlib

import nuke


@contextlib.contextmanager
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
