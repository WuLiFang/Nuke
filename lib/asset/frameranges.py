# -*- coding=UTF-8 -*-
"""Frame ranges.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re

import nuke

from nodeutil import is_node_deleted
from wlf.codectools import get_unicode as u
from pathlib2_unicode import PurePath

import filetools


class FrameRanges(object):
    """Wrap a object for get nuke.FrameRanges.

    Args:
        obj (any): Object contains frame_ranges.
            will use nuke.Root() instead when object is not support.
    """

    def __init__(self, obj=None):
        self._wrapped = obj
        self._cached_framerange = None
        self._list = None
        self._node_filename = (nuke.filename(obj)
                               if isinstance(obj, nuke.Node) else None)

    def to_frame_ranges(self):
        """Get nuke.FrameRanges from wrapped object."""

        if self._cached_framerange is not None:
            return self._cached_framerange

        obj = self._wrapped
        if isinstance(obj, nuke.FrameRanges):
            return obj

        ret = nuke.FrameRanges(self._frame_list())
        # Save result for some case.
        if isinstance(obj, (list, str, unicode, PurePath)):
            self._cached_framerange = ret

        return ret

    def _frame_list(self):
        from .footage import Footage

        obj = self._wrapped
        if obj is None:
            list_ = []
        elif isinstance(obj, (list, nuke.FrameRange)):
            list_ = list(obj)
        elif isinstance(obj, nuke.Root):
            list_ = self.from_root().to_frame_list()
        elif isinstance(obj, nuke.Node):
            # When node deleted or filename changed,
            # use previous result.
            if (is_node_deleted(obj)
                    or nuke.filename(obj) != self._node_filename):
                list_ = self._list or FrameRanges.from_node(
                    obj).to_frame_list()
            else:
                list_ = FrameRanges.from_node(obj).to_frame_list()
        elif isinstance(obj, Footage):
            list_ = obj.frame_ranges.toFrameList()
        elif isinstance(obj, FrameRanges):
            list_ = obj.wrapped.toFrameList()
        elif (isinstance(obj, (str, unicode))
              and re.match(r'^[\d -x]*$', u(obj))):
            # Parse Nuke frameranges string:
            list_ = self.from_text(obj).to_frame_list()

        elif isinstance(obj, (str, unicode, PurePath)):
            # Reconize as single frame
            list_ = self.from_path(obj).to_frame_list()
        else:
            raise TypeError
        self._list = list_
        return list_

    def __str__(self):
        return str(self.to_frame_ranges())

    def __add__(self, other):
        if isinstance(other, (nuke.FrameRanges, FrameRanges)):
            ret = FrameRanges(self.toFrameList() + other.toFrameList())
            ret.compact()
        else:
            raise TypeError(
                'FrameRanges.__add__ not support:{}'.format(type(other)))

        return ret

    def __getattr__(self, name):
        return getattr(self.to_frame_ranges(), name)

    def __nonzero__(self):
        return bool(self.to_frame_list())

    def to_frame_list(self):
        """nuke.FrameRanges will returns None if no frame in it.
        this will return a empty list.

        Returns:
            list: Frame list in this frame ranges.
        """
        ret = self.to_frame_ranges().toFrameList()
        if ret is None:
            ret = []
        return ret

    @classmethod
    def from_root(cls):
        """Get root frame ranges.
            (static result, init if need dynamic link.)
        """

        root = nuke.Root()
        first = int(root['first_frame'].value())
        last = int(root['last_frame'].value())
        if first > last:
            first, last = last, first
        list_ = range(first, last+1)
        return cls(list_)

    @classmethod
    def from_node(cls, node):
        """Get node frame ranges.
            (static result, init if need dynamic link.)
        """

        assert isinstance(node, nuke.Node)
        if is_node_deleted(node):
            return cls.from_root()
        if node.Class() == 'Read':
            first = node['first'].value()
            last = node['last'].value()
        else:
            first = node.firstFrame()
            last = node.lastFrame()

        if first > last:
            first, last = last, first
        list_ = range(first, last + 1)
        return cls(list_)

    @classmethod
    def from_text(cls, text):
        """"Get frame ranges from text.  """

        try:
            return cls(nuke.FrameRanges(text))
        except RuntimeError:
            raise ValueError

    @classmethod
    def from_path(cls, path):
        """"Get frame ranges from path.  """

        if (filetools.expand_frame(path, 1) ==
                filetools.expand_frame(path, 2)):
            return cls([1])
        return cls.from_root()
