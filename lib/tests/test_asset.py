# -*- coding=UTF-8 -*-
"""Test asset module.  """

from __future__ import absolute_import, unicode_literals, print_function
from unittest import TestCase, main

from tempfile import mkdtemp
import os
from random import sample


class DropFrameTestCase(TestCase):
    def setUp(self):
        self.temp_dir = mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_seq.%04d.exr')
        import nuke
        from wlf.path import Path
        frameranges = nuke.FrameRanges(
            list(xrange(91, 101)) + sample(xrange(91), 10))
        frameranges.compact()
        self.expected_dropframes = frameranges
        # create temp file.
        path = Path(self.temp_dir) / 'test_seq.%04d.exr'
        for i in set(xrange(91)).difference(frameranges.toFrameList()):
            with Path(path.with_frame(i)).open('w') as f:
                f.write(unicode(i))

    def _test_dropframe(self, filename):
        import nuke
        from lib.asset import Asset
        asset_ = Asset(filename)
        self.assertEqual(asset_.dropframes().toFrameList(),
                         self.expected_dropframes.toFrameList())
        self.assert_(asset_._dropframes)

    def test_dropframe_dry(self):
        self._test_dropframe(self.test_file)

    def test_dropframe_with_node(self):
        import nuke
        n = nuke.nodes.Read(file=self.test_file.replace('\\', '/'),
                            first=1,
                            last=100)
        assert isinstance(n, nuke.Node)
        self._test_dropframe(n)

    def tearDown(self):
        from wlf.path import Path
        try:
            path = Path(self.temp_dir)
            for i in path.iterdir():
                i.unlink()
            os.removedirs(str(path))
        except OSError as ex:
            raise RuntimeError(os.strerror(ex.errno) + str(ex))


if __name__ == '__main__':
    main()
