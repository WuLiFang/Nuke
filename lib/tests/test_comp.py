# -*- coding=UTF-8 -*-
"""Test comp package.  """

from __future__ import absolute_import, print_function, unicode_literals

import os
import random
import sys
import tempfile
from unittest import TestCase, main


class CompTestCase(TestCase):
    def test_comp(self):
        from comp import Comp


class BatchCompTestCase(TestCase):
    def test_get_comps(self):
        pass


class PrecompTestCase(TestCase):
    def test_from_node(self):
        pass

    def test_from_nodes(self):
        pass


if __name__ == '__main__':
    main()
