# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang._util import cast_str, assert_isinstance

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, TypeVar, Type

    T = TypeVar("T", bound=nuke.Knob)


def knob_of(node, name, class_):
    # type: (nuke.Node, Text, Type[T]) -> T
    return assert_isinstance(node.knob(cast_str(name)), class_)
