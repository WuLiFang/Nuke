# -*- coding=UTF-8 -*-
"""Nuke initiate test.  """
from __future__ import absolute_import, unicode_literals
from unittest import TestCase, main


class NukeToolsTestCase(TestCase):
    def test_utf8_obj(self):
        import nuke
        from nuketools import UTF8Object, utf8
        name = '测试节点'
        node = nuke.nodes.NoOp(name=utf8(name))
        utf8_obj = UTF8Object(node)
        for i in dir(node):
            self.assertIn(i, dir(utf8_obj))

        n = UTF8Object(nuke.toNode(utf8(name)))
        label = '中文标签'
        k = n['label']
        self.assertIsInstance(k, UTF8Object)
        k.setValue(label)
        self.assertEqual(n['label'].value(), label)


if __name__ == '__main__':

    main()
