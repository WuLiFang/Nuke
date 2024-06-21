# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


from wulifang._util import (
    cast_str,
    assert_isinstance,
    text_type,
    binary_type,
)
import nuke

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, TypeVar, Type, Optional

    T = TypeVar("T", bound=nuke.Knob)


def create_knob(
    _class,  # type: Type[T]
    _name,  # type: Text
    label=None,  # type: Optional[Text]
    flags=0,  # type: int
    value=None,  # type: object
    expression="",  # type: Text
    tooltip="",  # type: Text
):
    # type: (...) -> T

    k = _class(cast_str(_name))
    if flags:
        k.setFlag(flags)
    if label is not None:
        k.setLabel(cast_str(label))
    if value is not None:
        if isinstance(k, (nuke.String_Knob, nuke.Text_Knob)):
            k.setValue(cast_str(assert_isinstance(value, (text_type, binary_type))))
        elif isinstance(k, nuke.Array_Knob):
            if isinstance(value, (int, float)):
                k.setValue(value)
            else:
                values = tuple(assert_isinstance(i, (int, float)) for i in assert_isinstance(value, (list, tuple)))  # type: ignore
                k.setValue(values)
        elif isinstance(k, nuke.Boolean_Knob):
            k.setValue(assert_isinstance(value, bool))
        else:
            raise RuntimeError("not implemented: %r", _class)
    if expression:
        k.setExpression(cast_str(expression))
    if tooltip:
        k.setTooltip(cast_str(tooltip))
    return k
