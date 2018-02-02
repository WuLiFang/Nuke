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
        self.test_file = os.path.join(self.temp_dir, 'test_seq.%04d.exr')
        self.expected_dropframes = nuke.FrameRanges(
            sample(xrange(1, 91), 10) + list(xrange(91, 101)))
        self.expected_dropframes.compact()

        # Create temp file.
        path = Path(self.temp_dir) / 'test_seq.%04d.exr'
        for i in set(xrange(1, 91)).difference(self.expected_dropframes.toFrameList()):
            with Path(path.with_frame(i)).open('w') as f:
                f.write(unicode(i))

        # Create node.
        self.assertFalse(nuke.allNodes())
        self.node = nuke.nodes.Read(file=self.test_file.replace('\\', '/'),
                                    first=1,
                                    last=100)

    def _test_dropframe(self, filename):
        from lib.asset import Asset
        asset_ = Asset(filename)
        self.assertEqual(asset_.dropframes().toFrameList(),
                         self.expected_dropframes.toFrameList())
        self.assert_(asset_._dropframes)

    def test_dropframe_dry(self):
        self._test_dropframe(self.test_file)

    def test_dropframe_with_node(self):
        self._test_dropframe(self.node)

    def test_warn(self):
        from lib.asset import warn_dropframes
        warn_dropframes()

    def tearDown(self):
        # Clean up files.
        try:
            path = Path(self.temp_dir)
            for i in path.iterdir():
                i.unlink()
            os.removedirs(str(path))
        except OSError as ex:
            raise RuntimeError(os.strerror(ex.errno) + str(ex))

        # Clear working script.
        nuke.delete(self.node)


if __name__ == '__main__':
    main()
