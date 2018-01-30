# -*- coding=UTF-8 -*-
"""Nuke tools for programing.  """
from __future__ import absolute_import, unicode_literals

from wlf.path import get_encoded


def utf8(obj):
    """Convert unicode to str with utf8 encoding.  """

    if isinstance(obj, (str, unicode)):
        return get_encoded(obj, 'utf-8')
    return obj


def iutf8(iterable):
    """Convert unicode to utf8 string for @iterable.  """

    for i in iterable:
        yield utf8(i)


def utf8_dict(dict_):
    """Return new dict with @dict_ keys has been
    converted from unicode to utf8 string.
    """
    assert isinstance(dict_, dict)

    ret = dict(dict_)
    for i in ret:
        ret[i] = utf8(ret[i])
    return ret
