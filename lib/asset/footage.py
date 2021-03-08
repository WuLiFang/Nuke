# -*- coding=UTF-8 -*-
"""Footage asset.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

import nuke

import nuketools
from wlf.codectools import get_unicode as u
from pathlib2_unicode import Path

from . import cache, core
from .frameranges import FrameRanges

LOGGER = logging.getLogger(__name__)

import filetools
class Footage(object):
    """Asset for nuke node.  """

    def __new__(cls, filename, frame_ranges=None):
        # Skip new from other Asset objet.
        if isinstance(filename, Footage):
            return filename

        frame_ranges = filename if frame_ranges is None else frame_ranges
        filename = cls.filename_factory(filename)

        # Try find cached asset.
        for i in core.CACHED_ASSET:
            assert isinstance(i, Footage)
            if u(i.filename) == u(filename):
                if filetools.is_sequence_name(filename):
                    i.frame_ranges += FrameRanges(frame_ranges)
                return i
        return super(Footage, cls).__new__(cls)

    def __init__(self, filename, frame_ranges=None):
        # Skip init cached Asset objet.
        if self in core.CACHED_ASSET:
            return

        frame_ranges = filename if frame_ranges is None else frame_ranges
        filename = self.filename_factory(filename)
        self.filename = filename
        self.frame_ranges = FrameRanges(frame_ranges)

        core.CACHED_ASSET.add(self)

    def __unicode__(self):
        return '素材: {0.filename} {0.frame_ranges}'.format(self)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    @classmethod
    def filename_factory(cls, obj):
        """get filename from a object.

        Args:
            obj (str or unicode or nuke.Node): Object contain filename.

        Returns:
            Path: filename path.
        """

        filename = obj
        if isinstance(obj, nuke.Node):
            filename = nuke.filename(obj)
        elif isinstance(obj, Footage):
            filename = obj.filename
        elif isinstance(obj, (str, unicode)):
            pass
        else:
            raise TypeError('can not use as filename: {}'.format(type(obj)))
        path = Path(u(filename))
        return path
    _last_missing_frame_warn_msg = None

    def missing_frames(self, frame_ranges=None, timeout=-1):
        """Get missing frame ranges compare to frame_list.

        Args:
            frame_list (Iterable[int]
                or nuke.Node
                or nuke.FrameRanges, optional): Defaults to None.
                check file exsits with these frames,
                None mean return whole missing frame ranges.

        Returns:
            Optional[FrameRanges] : missing frame ranges,
                None means result not ready.
        """
        LOGGER.debug("checking missing frames: %s", self.filename)
        if frame_ranges is None:
            frame_ranges = self.frame_ranges
        else:
            frame_ranges = FrameRanges(frame_ranges)

        # Update if need.
        missing_frames = []
        is_processing = False
        for f in frame_ranges.toFrameList():
            path = filetools.expand_frame(self.filename, f)
            result = cache.is_file_exist(path, timeout=timeout)
            if result is None:
                is_processing = True
                continue
            if result is False:
                missing_frames.append(f)
        if is_processing:
            return None

        ret = FrameRanges(missing_frames)
        ret.compact()
        msg = '{} 缺帧: {}'.format(self, ret)
        if ret and msg != self._last_missing_frame_warn_msg:
            nuke.warning(nuketools.utf8(msg))
            self._last_missing_frame_warn_msg = msg
        return ret
