# -*- coding=UTF-8 -*-
"""Nuke tools for programing.  """
from __future__ import absolute_import, unicode_literals

from functools import wraps

from wlf.path import get_encoded


class UTF8Object(object):
    """UTF8Wraper for nuke object.  """

    def __new__(cls, obj):
        if obj is None or isinstance(obj, (float, int, UTF8Object)):
            return obj
        return super(UTF8Object, cls).__new__(cls, obj)

    def __init__(self, obj):
        if obj is self:
            return
        self.obj = obj
        for i in dir(obj):
            if not i.startswith('_') and i in self.__dict__:
                continue
            try:
                self.__dict__[i] = utf8(getattr(obj, i))
            except AttributeError:
                self.__dict__[i] = getattr(obj, i)

    def __repr__(self):
        return get_encoded('|utf8 {}|' .format(repr(self.obj).decode('utf-8')))

    def __dir__(self):
        return dir(self.obj)

    def __getitem__(self, name):
        return utf8(self.obj.__getitem__(name))


def utf8(obj):
    """Convert unicode to str with utf8 encoding.  """

    if isinstance(obj, (str, unicode)):
        return get_encoded(obj, 'utf-8')
    elif isinstance(obj, dict):
        return utf8_dict(obj)
    if callable(obj):
        return utf8_func(obj)
    return UTF8Object(obj)


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


def utf8_func(func):
    """(Decorator)Wrap utf8 only @func to support unicode.  """

    @wraps(func)
    def _func(*args, **kwargs):
        args = tuple(utf8(i) for i in args)
        kwargs = utf8_dict(kwargs)
        try:
            ret = func(*args, **kwargs)
        except:
            import nuke
            nuke.message(repr(func))
            raise
        if isinstance(ret, str):
            ret = ret.decode('utf-8')
        elif callable(ret):
            ret = UTF8Object(ret)
        return ret

    return _func
