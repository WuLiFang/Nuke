# -*- coding=UTF-8 -*-
# pyright: ignore

from __future__ import absolute_import, division, print_function, unicode_literals


def assert_isinstance(object, class_or_tuple):
    """raise CastError when object is not isinstance of given class.

    Args:
        object: object to test
        class_or_tuple: second arg of `isinstance`

    Raises:
        CastError: When object is not match

    Returns:
        object unchanged
    """
    assert isinstance(
        object, class_or_tuple
    ), "unexpected instance type, expected=%s, actual=%s" % (
        class_or_tuple,
        type(object),
    )
    return object
