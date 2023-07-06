# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import nuke

from ._knob_of import knob_of


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, TypeVar, Type, Optional

    T = TypeVar("T", bound=nuke.Knob)


def optional_knob_of(node, name, class_):
    # type: (nuke.Node, Text, Type[T]) -> Optional[T]
    try:
        return knob_of(node, name, class_)
    except (NameError, AssertionError):
        pass
