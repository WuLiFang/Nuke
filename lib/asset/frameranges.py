# -*- coding=UTF-8 -*-
"""Frame ranges.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re

import nuke

from wlf.codectools import get_unicode as u
from wlf.path import PurePath


class FrameRanges(object):
    """Wrap a object for get nuke.FrameRanges.

    Args:
        obj (any): Object contains frame_ranges.
            will use nuke.Root() instead when object is not support.
    """

    def __init__(self, obj=None):
        self._wrapped = obj
        self._list = None
        self._node_filename = (nuke.filename(obj)
                               if isinstance(obj, nuke.Node) else None)

    @property
    def wrapped(self):
        """Get frame range from wrapped object."""

        from .footage import Footage

        obj = self._wrapped
        if isinstance(obj, nuke.FrameRanges):
            return obj

        # Get frame_list from obj
        try:
            # LOGGER.debug('get from %s', type(obj))
            if self._wrapped is None:
                raise TypeError
            elif isinstance(obj, (list, nuke.FrameRange)):
                list_ = list(obj)
            elif isinstance(obj, nuke.Root):
                first = int(obj['first_frame'].value())
                last = int(obj['last_frame'].value())
                if first > last:
                    first, last = last, first
                list_ = range(first, last+1)
            elif isinstance(obj, nuke.Node):
                is_deleted = True
                try:
                    repr(obj)
                    is_deleted = False
                except ValueError:
                    pass
                # When node deleted or filename changed,
                # use previous result.
                if (is_deleted
                        or nuke.filename(obj) != self._node_filename):
                    list_ = self._list
                    if list_ is None:
                        raise TypeError
                else:
                    first = obj.firstFrame()
                    last = obj.lastFrame()
                    if first > last:
                        first, last = last, first
                    list_ = range(first, last+1)
            elif isinstance(obj, Footage):
                list_ = obj.frame_ranges.toFrameList()
            elif isinstance(obj, FrameRanges):
                list_ = obj.wrapped.toFrameList()
            elif (isinstance(obj, (str, unicode))
                  and re.match(r'^[\d -x]*$', u(obj))):
                # Parse Nuke frameranges string:
                try:
                    list_ = nuke.FrameRanges(obj).toFrameList()
                except RuntimeError:
                    raise TypeError
            elif isinstance(obj, (str, unicode, PurePath)):
                # Reconize as single frame
                path = PurePath(obj)
                if path.with_frame(1) == path.with_frame(2):
                    list_ = [1]
                else:
                    raise TypeError
            else:
                raise TypeError

            self._list = list_
            ret = nuke.FrameRanges(list_)

            # Save result for some case.
            if isinstance(obj, (list, str, unicode, PurePath)):
                self._wrapped = ret

            return ret
        except TypeError:
            self._wrapped = None
            return self.from_root()

    def __str__(self):
        return str(self.wrapped)

    def __add__(self, other):
        if isinstance(other, (nuke.FrameRanges, FrameRanges)):
            ret = FrameRanges(self.toFrameList() + other.toFrameList())
            ret.compact()
        else:
            raise TypeError(
                'FrameRanges.__add__ not support:{}'.format(type(other)))

        return ret

    def __getattr__(self, name):
        return getattr(self.wrapped, name)

    def __nonzero__(self):
        return bool(self.to_frame_list())

    def to_frame_list(self):
        """nuke.FrameRanges will returns None if no frame in it.
        this will return a empty list.

        Returns:
            list: Frame list in this frame ranges.
        """
        ret = self.wrapped.toFrameList()
        if ret is None:
            ret = []
        return ret

    @classmethod
    def from_root(cls):
        """Get root frame range.  """

        root = nuke.Root()
        first = root['first_frame'].value()
        last = root['last_frame'].value()
        ret = nuke.FrameRanges(first, last, 1)
        ret = FrameRanges(ret)
        return FrameRanges(nuke.Root())
