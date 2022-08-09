# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals

from wulifang.vendor import six

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Union


def text(v, encoding="utf-8", errors="strict"):
    # type: (Union[Text, bytes], Text, Text) -> Text

    if isinstance(v, six.text_type):
        return v
    return v.decode(encoding, errors)


def binary(v, encoding="utf-8", errors="strict"):
    # type: (Union[Text, bytes], Text, Text) -> bytes
    if isinstance(v, six.binary_type):
        return v
    return v.encode(encoding, errors)
