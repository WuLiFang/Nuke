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
    def _pop(self):
        from asset import Asset
        return Asset('test测试')

    def test_nest(self):
        from asset import Asset
        first = self._pop()
        self.assertIs(first, Asset(first))

    def test_cache(self):
        first = self._pop()
        self.assertIs(first, self._pop())

    def test_auto_framerange(self):
        from asset import Asset
        first = Asset('test测试')
        self.assertEqual(str(first.frame_ranges), '1-1')
        last = Asset('test测试.%04d.exr')
        self.assertEqual(str(last.frame_ranges), '1-100')

    def test_expand_range(self):
        from asset import Asset

        first = Asset('test测试')
        print(first.frame_ranges)
        last = Asset('test测试', '2-200')
        print(last.frame_ranges)
        print(first.frame_ranges)


class DropFrameTestCase(TestCase):
    def setUp(self):

        self.temp_dir = mkdtemp()
        self.addCleanup(os.removedirs, self.temp_dir)
        self.test_file = os.path.join(self.temp_dir, 'test_seq.%04d.exr')
        self.expected_missing_frames = nuke.FrameRanges(
            sample(xrange(1, 91), 10) + list(xrange(91, 101)))
        self.expected_missing_frames.compact()

        # Create temp file.
        path = Path(Path(self.temp_dir) / 'test_seq.%04d.exr')
        for i in set(xrange(1, 91)).difference(self.expected_missing_frames.toFrameList()):
            j = Path(path.with_frame(i))
            with j.open('w') as f:
                f.write(unicode(i))
            self.addCleanup(j.unlink)

        # Create node.
        self.node = nuke.nodes.Read(file=self.test_file.replace('\\', '/'),
                                    first=1,
                                    last=100)

    def _test_missing_frame(self, filename):
        from asset import Asset, CachedMissingFrames
        asset_ = Asset(filename)

        def _pop():
            ret = asset_.missing_frames()
            self.assertEqual(ret.toFrameList(),
                             self.expected_missing_frames.toFrameList())
            return ret

        _pop()

        # test cache
        cached = asset_._missing_frames
        self.assertIsInstance(cached, CachedMissingFrames)
        _pop()
        self.assertIs(cached, asset_._missing_frames)
        asset_.update_interval = -1
        _pop()
        self.assertIsNot(cached, asset_._missing_frames)

    def test_missing_frame_dry(self):
        self._test_missing_frame(self.test_file)

    def test_missing_frame_with_node(self):
        self._test_missing_frame(self.node)

    def test_get_missing_frames(self):
        from asset import Assets, MissingFramesDict
        result = Assets.all().missing_frames_dict()
        self.assertIsInstance(result, MissingFramesDict)
        self.assertIsInstance(result.as_html(), unicode)

    def test_warn_missing_frames(self):
        from asset import warn_missing_frames
        warn_missing_frames()


if __name__ == '__main__':
    main()
