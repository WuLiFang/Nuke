# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text
    from .._types.aov_spec import AOVLayerCreationMethod, AOVLayerCreationOperation


class AOVLayerCreationMethodImpl(object):
    def __init__(
        self,
        _operation,  # type: AOVLayerCreationOperation
        _inputs,  # type: tuple[Text, ...]
    ):
        # type: (...) -> None
        self.operation = _operation # type: AOVLayerCreationOperation
        self.inputs = _inputs


def _(v):
    # type: (AOVLayerCreationMethodImpl) ->AOVLayerCreationMethod
    return v
