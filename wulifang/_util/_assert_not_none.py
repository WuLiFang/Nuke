# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Optional, TypeVar
    T = TypeVar("T")


def assert_not_none(v):
    # type: (Optional[T]) -> T
    assert v is not None, "should not be none"
    return v
