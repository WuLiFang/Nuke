# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals


from contextlib import contextmanager

import nuke


@contextmanager
def ignore_modification():
    """Restore modified flag after action finished."""

    root = nuke.root()
    before = root.modified()
    try:
        yield
    finally:
        root.setModified(before)
