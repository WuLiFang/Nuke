# -*- coding=UTF-8 -*-
"""Nuke initiate test.  """
from __future__ import absolute_import
from unittest import TestCase, main


class NukeTestCase(TestCase):

    def test_init(self):
        import nuke


if __name__ == '__main__':
    main()
