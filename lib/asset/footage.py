# -*- coding=UTF-8 -*-
"""Footage asset.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import multiprocessing.dummy as multiprocessing
import os
import time

import nuke

from nuketools import utf8
from wlf.codectools import get_unicode as u
from wlf.path import Path

from . import core
from .frameranges import FrameRanges
from .model import CachedMissingFrames

LOGGER = logging.getLogger(__name__)


class Footage(object):
    """Asset for nuke node.  """

    update_interval = 10

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
                if filename.with_frame(1) != filename.with_frame(2):
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
        self._missing_frames = None

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
            wlf.path.Path: filename path.
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

    def missing_frames(self, frame_ranges=None):
        """Get missing frame ranges compare to frame_list.

        Args:
            frame_list (Iterable[int]
                or nuke.Node
                or nuke.FrameRanges, optional): Defaults to None.
                check file exsits with these frames,
                None mean return whole missing frame ranges.

        Returns:
            FrameRanges: missing frame ranges.
        """

        if frame_ranges is None:
            frame_ranges = self.frame_ranges
        else:
            frame_ranges = FrameRanges(frame_ranges)

        # Update if need.
        if (not isinstance(self._missing_frames, CachedMissingFrames)
                or time.time() - self._missing_frames.timestamp
                > self.update_interval):
            self._update_missing_frame()

        assert isinstance(self._missing_frames, CachedMissingFrames)
        cached = self._missing_frames.frame_ranges

        ret = FrameRanges([i for i in cached.to_frame_list()
                           if i in frame_ranges.to_frame_list()])
        ret.compact()
        return ret

    def _update_missing_frame(self):
        ret = FrameRanges([])
        checked = set()
        frames = self.frame_ranges.toFrameList()

        def _check(frame):
            try:
                path = Path(self.filename.with_frame(frame))
                if path in checked:
                    return
                if not path.is_file():
                    ret.add([frame])
                checked.add(path)
            except OSError as ex:
                LOGGER.error(os.strerror(ex.errno), exc_info=True)

        pool = multiprocessing.Pool()
        pool.map(_check, frames)
        pool.close()
        pool.join()

        ret.compact()
        self._missing_frames = CachedMissingFrames(ret, time.time())
        if ret:
            msg = '{} 缺帧: {}'.format(self, ret)
            nuke.warning(utf8(msg))
        return ret
