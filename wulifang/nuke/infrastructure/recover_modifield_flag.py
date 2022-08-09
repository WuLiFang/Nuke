# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals


from contextlib import contextmanager
import nuke


@contextmanager
def recover_modifield_flag():
    """Restore modifield flag after action finished."""

    root = nuke.Root()
    assert isinstance(root, nuke.Root)
    before = root.modified()
    try:
        yield
    finally:
        root.setModified(before)
