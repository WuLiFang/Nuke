# -*- coding=UTF-8 -*-
"""Test comp package.  """

from __future__ import absolute_import, print_function, unicode_literals

import os
import random
import sys
import tempfile
from unittest import TestCase, main, skip

import pytest

pytestmark = [pytest.mark.skipif(
    sys.platform != 'win32', reason='Only support windows for now.')]


@skip('TODO')
class CompTestCase(TestCase):
    def test_comp(self):
        from comp import Comp


class BatchCompTestCase(TestCase):
    @skip('TODO')
    def test_get_comps(self):
        pass

    @skip('TODO: log path may not exists')
    def test_report(self):
        from comp import BatchComp

        BatchComp.generate_report({'test1': 'asd',
                                   'test2中文': 'test2中文',
                                   'test3\\n\\a': 'test3<br>sad'})


@skip('TODO')
class PrecompTestCase(TestCase):
    def test_from_node(self):
        pass

    def test_from_nodes(self):
        pass


if __name__ == '__main__':
    main()
