# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text
    from .._types.aov_spec import AOVLayerCreationMethod, AOVLayerOperation, AOVLayer


class AOVLayerImpl(object):
    def __init__(
        self,
        _name,  # type: Text
        _label,  # type: Text
        _operation,  # type: AOVLayerOperation
        alias=(),  # type: tuple[Text, ...]
        creation_methods=(),  # type: tuple[AOVLayerCreationMethod,...]
    ):
        # type: (...) -> None
        self.name = _name
        self.alias = alias
        self.label = _label
        self.operation = _operation  # type: AOVLayerOperation
        self.creation_methods = creation_methods


def _(v):
    # type: (AOVLayerImpl) -> AOVLayer
    return v
