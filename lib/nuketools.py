# -*- coding=UTF-8 -*-
"""Nuke tools for programing.  """
from __future__ import absolute_import, unicode_literals

import logging
import threading
from functools import wraps

import nuke
from collections import Iterable

from wlf.decorators import run_in_main_thread
from wlf.path import get_encoded

LOGGER = logging.getLogger('com.wlf.nuketools')


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


def undoable_func(name=None):
    """(Decorator)Record nuke undo set for @func.   """

    def _wrap(func):

        @wraps(func)
        def _func(*args, **kwargs):
            _name = name if name is not None else func.__name__
            run_in_main_thread(nuke.Undo.begin)(utf8(_name))

            try:
                ret = func(*args, **kwargs)
                if not isinstance(ret, threading.Thread):
                    # Async function should call nuke.Undo.end by itself.
                    run_in_main_thread(nuke.Undo.end)()
                else:
                    LOGGER.warning(
                        'Async function should implement undoable itself.')
                return ret
            except:
                run_in_main_thread(nuke.Undo.cancel)()
                raise

        return _func

    return _wrap


class Nodes(list):
    """Optmized list for nuke.Node.  """

    def __init__(self, nodes=None):
        if nodes is None:
            nodes = []
        if isinstance(nodes, nuke.Node):
            nodes = [nodes]

        list.__init__(self, nodes)

    @property
    def xpos(self):
        """The x position.  """
        return min(n.xpos() for n in self)

    @xpos.setter
    def xpos(self, value):
        extend_x = value - self.xpos
        for n in self:
            xpos = n.xpos() + extend_x
            n.setXpos(xpos)

    @property
    def ypos(self):
        """The y position.  """
        return min([node.ypos() for node in self])

    @ypos.setter
    def ypos(self, value):
        extend_y = value - self.ypos
        for n in self:
            ypos = n.ypos() + extend_y
            n.setYpos(ypos)

    @property
    def width(self):
        """The total width of all nodes.  """
        return self.right - self.xpos

    @property
    def max_width(self):
        """The node width max value in this."""
        return max(n.screenWidth() for n in self)

    @property
    def height(self):
        """The total height of all nodes.  """
        return self.bottom - self.ypos

    @property
    def bottom(self):
        """The bottom border of all nodes.  """
        return max([node.ypos() + node.screenHeight()
                    for node in self])

    @bottom.setter
    def bottom(self, value):
        extend_y = value - self.bottom
        for n in self:
            ypos = n.ypos() + extend_y
            n.setYpos(ypos)

    @property
    def right(self):
        """The right border of all nodes.  """
        return max(n.xpos() + n.screenWidth() for n in self)

    @right.setter
    def right(self, value):
        extend_x = value - self.right
        for n in self:
            xpos = n.xpos() + extend_x
            n.setXpos(xpos)

    def set_position(self, xpos=None, ypos=None):
        """Move nodes to given @xpos, @ypos.  """
        if xpos:
            self.xpos = xpos
        if ypos:
            self.ypos = ypos

    def autoplace(self):
        """Auto place nodes."""

        from orgnize import autoplace
        autoplace(self)

    def endnodes(self):
        """Return Nodes that has no contained downstream founded in given nodes.  """
        ret = set(n for n in self if n.Class() not in ('Viewer',))
        other = list(n for n in self if n not in ret)

        for n in list(ret):
            dep = n.dependencies(nuke.INPUTS)
            if set(self).intersection(dep):
                ret.difference_update(dep)
        ret = sorted(ret, key=lambda x: len(
            get_upstream_nodes(x)), reverse=True)
        ret.extend(other)
        return ret

    def disable(self):
        """Disable all.  """

        for n in self:
            try:
                n['disable'].setValue(True)
            except NameError:
                continue

    def enable(self):
        """Enable all.  """

        for n in self:
            try:
                n['disable'].setValue(False)
            except NameError:
                continue


def get_upstream_nodes(nodes, flags=nuke.INPUTS | nuke.HIDDEN_INPUTS):
    """ Return all nodes in the tree of the node. """
    ret = set()
    if isinstance(nodes, nuke.Node):
        nodes = [nodes]

    nodes = list(nodes)
    while nodes:
        deps = nuke.dependencies(nodes, flags)
        nodes = [n for n in deps if n not in ret and n not in nodes]
        ret.update(set(deps))
    return ret


def abort_modified(func):
    """(Decorator)Abort function when project has been modified."""

    @wraps(func)
    def _func():
        if nuke.Root().modified():
            return False
        return func()
    return _func
