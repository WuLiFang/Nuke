# -*- coding=UTF-8 -*-
"""Footage monitor.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from multiprocessing.dummy import Pool

import nuke

from wlf.codectools import get_encoded as e
from wlf.codectools import get_unicode as u
from wlf.decorators import run_with_clock

from .footage import Footage
from .model import MissingFramesDict


class FootagesMonitor(list):
    """Multiple Asset. Get assets from a obj.

    Args:
        obj (Assets supported types): object may contain multiple assets.
        is_strict (bool) : Defaults to False, strict mode switch.

    Raises:
        ValueError: when `is_strict` is True and can not get assets from `obj`.

    Returns:
        list[Asset]: List of asset in `obj`, or all_assets as default.
    """

    def __init__(self, obj, is_strict=False):
        if isinstance(obj, FootagesMonitor):
            list_ = obj
        else:
            try:
                list_ = set(Footage(obj))
            except TypeError:
                try:
                    list_ = list(Footage(i) for i in obj)
                except TypeError:
                    if is_strict:
                        raise TypeError('Not supported type.', type(obj))
                    list_ = []
        super(FootagesMonitor, self).__init__(set(list_))

    def __str__(self):
        return e(self.__unicode__())

    def __unicode__(self):
        return [u(i) for i in self]

    @classmethod
    def all(cls):
        """Get all assets current using.

        Returns:
            Assets: current assets.
        """

        return cls(nuke.allNodes('Read'))

    @run_with_clock('检查缺帧')
    def missing_frames_dict(self):
        """Get missing_frames from assets.

        Decorators:
            run_with_clock

        Returns:
            DropFramesDict: Dict of (asset, missing_frames) pair.
        """

        ret = MissingFramesDict()

        def _run(asset):
            assert isinstance(asset, Footage)
            try:
                missing_frames = asset.missing_frames()
                if missing_frames:
                    key = u(asset.filename.as_posix())
                    if key in ret:
                        ret[key].add(missing_frames)
                    else:
                        ret[key] = missing_frames
            except:
                import traceback
                raise RuntimeError(traceback.format_exc())

        if self:
            pool = Pool()
            pool.map(_run, self)
            pool.close()
            pool.join()

        return ret
