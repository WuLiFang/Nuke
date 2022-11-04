# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


import contextlib
from typing import Text

from ._force_rename import force_rename


@contextlib.contextmanager
def atomic_save_path(
    path,
    temp_suffix=".tmp",
    backup_suffix="",
):
    # type: (Text, Text, Text) -> ...
    tmp_path = path + temp_suffix
    yield tmp_path
    if backup_suffix:
        backup_path = path + backup_suffix
        try:
            force_rename(path, backup_path)
        except FileNotFoundError:
            pass
    force_rename(tmp_path, path)
