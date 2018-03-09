# -*- coding=UTF-8 -*-
"""Test `cgtwn` module.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from unittest import TestCase, main


class TaskTestCase(TestCase):
    def test_init(self):
        from cgtwn import Task
        select = Task('MT_EP06_06_sc013')
        self.assertEqual(len(select), 1)


if __name__ == '__main__':
    main()
