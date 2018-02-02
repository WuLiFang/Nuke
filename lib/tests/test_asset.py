# -*- coding=UTF-8 -*-
"""Test asset module.  """

from __future__ import absolute_import, print_function, unicode_literals

import os
from random import sample
from tempfile import mkdtemp
from unittest import TestCase, main

import nuke

from wlf.path import Path


class AssetTestCase(TestCase):
    def test_cache(self):
        from lib.asset import Asset

        def _pop():
            return Asset('test测试')
        first = _pop()
        self.assertIs(first, _pop())


class DropFrameTestCase(TestCase):
    def setUp(self):

        self.temp_dir = mkdtemp()
        self.addCleanup(os.removedirs, self.temp_dir)
        self.test_file = os.path.join(self.temp_dir, 'test_seq.%04d.exr')
        self.expected_dropframes = nuke.FrameRanges(
            sample(xrange(1, 91), 10) + list(xrange(91, 101)))
        self.expected_dropframes.compact()

        # Create temp file.
        path = Path(self.temp_dir) / 'test_seq.%04d.exr'
        for i in set(xrange(1, 91)).difference(self.expected_dropframes.toFrameList()):
            j = Path(path.with_frame(i))
            with j.open('w') as f:
                f.write(unicode(i))
            self.addCleanup(j.unlink)

        # Create node.
        nuke.scriptClear()
        self.node = nuke.nodes.Read(file=self.test_file.replace('\\', '/'),
                                    first=1,
                                    last=100)

    def _test_dropframe(self, filename):
        from lib.asset import Asset, CachedDropframes
        asset_ = Asset(filename)

        def _pop():
            ret = asset_.dropframes()
            self.assertEqual(ret.toFrameList(),
                             self.expected_dropframes.toFrameList())
            return ret

        _pop()

        # test cache
        cached = asset_._dropframes
        self.assertIsInstance(cached, CachedDropframes)
        _pop()
        self.assertIs(cached, asset_._dropframes)
        asset_.update_interval = 0
        _pop()
        self.assertIsNot(cached, asset_._dropframes)

    def test_dropframe_dry(self):
        self._test_dropframe(self.test_file)

    def test_dropframe_with_node(self):
        self._test_dropframe(self.node)

    def test_warn(self):
        from lib.asset import warn_dropframes
        warn_dropframes()


if __name__ == '__main__':
    main()
