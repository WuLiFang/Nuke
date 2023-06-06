# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Optional, Iterator


import nuke


def iter_deep_all_nodes(root=None):
    # type: (Optional[nuke.Group]) -> Iterator[nuke.Node]
    for n in (root or nuke.Root()).nodes():
        if isinstance(n, nuke.Group):
            for i in iter_deep_all_nodes(n):
                yield i
        yield n
