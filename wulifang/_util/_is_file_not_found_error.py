# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

from ._compat import PY2


def is_file_not_found_error(err):
    # type: (Exception) -> bool
    if PY2:
        import errno

        return isinstance(err, (OSError, IOError)) and (err.errno == errno.ENOENT)

    return isinstance(err, FileNotFoundError)
