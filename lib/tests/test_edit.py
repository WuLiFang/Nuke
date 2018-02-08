# -*- coding=UTF-8 -*-
"""Test edit module.  """

from __future__ import absolute_import, print_function, unicode_literals

import os
import random
import sys
import tempfile
from unittest import TestCase, main

import nuke


class EditTestCase(TestCase):
    def setUp(self):
        nuke.scriptClear(True)

    def test_add_channel(self):
        from edit import add_channel
        add_channel(b'test.channel')
        self.assertIn('test.channel', nuke.Root().channels())
        add_channel(u'test.channel2')
        self.assertIn('test.channel2', nuke.Root().channels())
        self.assertRaises(ValueError,
                          add_channel, 'test.channel3中文')
        self.assertRaises(ValueError,
                          add_channel, b'test.channel4中文')
        add_channel('test channel5')
        self.assertIn('other.test channel5', nuke.Root().channels())
        self.assertRaises(ValueError,
                          add_channel, 'test.channel6.test')

    def test_add_layer(self):
        from edit import add_layer
        self.assertNotIn('test', nuke.layers())
        add_layer('test')
        self.assertIn('test', nuke.layers())
        for i in ('test.red', 'test.green', 'test.blue', 'test.alpha'):
            self.assertIn(i, nuke.channels())

    def test_doctest(self):
        from doctest import testmod
        import edit
        self.assertFalse(testmod(edit).failed, 'Doctest failed')

    def test_named_copy(self):
        from edit import named_copy
        # Normal case.
        n = nuke.nodes.Constant()
        n = nuke.nodes.AddChannels(
            inputs=[n],
            channels='mask.a',
            channels2='depth.Z',
            channels3='forward.v',
        )
        names_dict = {
            'r': 'test1',
            'green': 'test2',
            'rgba.blue': 'test3',
            'rgba.alpha': 'test4',
            'depth.Z': 'test5 test',
            'forward.v': 'test6测试',
            'mask.a': 'test7.test',
        }
        n = named_copy(n, names_dict)
        self.assertIsInstance(n, nuke.Node)
        self.assertEqual(n.Class(), 'Copy')
        self.assertEqual(len(nuke.allNodes('Copy')),
                         ((len(names_dict) - 1) / 4) + 1)

        self.assertEqual(n.channels(),
                         [b'rgba.red', b'rgba.green',
                          b'rgba.blue', b'rgba.alpha',
                          b'depth.Z', b'forward.v',
                          b'mask.a',
                          # Ordered according input channels.
                          b'mask_extra.test5_test',
                          b'mask_extra.test6??',
                          b'test7.test',
                          b'mask_extra.test1', b'mask_extra.test2',
                          b'mask_extra.test3', b'mask_extra.test4',
                          ])
        #　Empty names_dict.
        last = named_copy(n, {})
        self.assertIs(n, last)

    def test_replace_node(self):
        from edit import replace_node
        const = nuke.nodes.Constant()
        for _ in xrange(20):
            nuke.nodes.Grade(inputs=[const])
        nodes = nuke.allNodes('Grade')
        self.assertEqual(len(nodes), 20)
        noop = nuke.nodes.NoOp()
        replace_node(const, noop)
        for i in nodes:
            self.assertIs(i.input(0), noop)

        self.assertRaises(TypeError, replace_node, noop, 1)
        self.assertRaises(TypeError, replace_node, 1, noop)

    def test_get_min_max(self):
        from edit import get_min_max
        for _ in xrange(5):
            color = random.random()
            n = nuke.nodes.AddChannels(
                channels='depth.Z',
                color=color)
            result = get_min_max(n, 'depth.Z')
            self.assertAlmostEqual(result[0], color)
            self.assertAlmostEqual(result[1], color)

    def test_random_glcolor(self):
        from edit import set_random_glcolor
        n = nuke.nodes.NoOp()
        self.assertFalse(n['gl_color'].value())
        for _ in xrange(10):
            set_random_glcolor(n)
            self.assert_(n['gl_color'].value())

    def test_clear_selection(self):
        from edit import clear_selection
        for _ in xrange(20):
            nuke.nodes.NoOp(selected=True)
        self.assertEqual(len(nuke.selectedNodes()), 20)
        clear_selection()
        self.assertFalse(nuke.selectedNodes())

    def test_split_layers(self):
        from edit import split_layers

        n = nuke.nodes.Constant()
        nuke.Layer('test', ['test.red', 'test.green',
                            'test.blue', 'test.alpha'])
        nuke.Layer('test2', ['test2.red', 'test2.green', 'test2.blue'])
        nuke.Layer('test3', ['test3.u', 'test3.v'])
        nuke.Layer('test4', ['test4.Z'])
        layers = ('test', 'test2', 'test3', 'test4')

        for i in layers:
            n = nuke.nodes.AddChannels(inputs=[n], channels=i)
        for is_postage in (True, False):
            n['postage_stamp'].setValue(is_postage)
            result = split_layers(n)
            self.assertEqual(len(result), 4)
            for i in result:
                self.assertIsInstance(i, nuke.Node)
                self.assertEqual(i.Class(), 'Shuffle')
                self.assertIn(i['in'].value(), layers)
                self.assertEqual(i['postage_stamp'].value(), is_postage)

    def test_shuffle_rgba(self):
        from edit import shuffle_rgba
        rgba = ('red', 'green', 'blue', 'alpha')

        n = nuke.nodes.Constant()
        for is_postage in (True, False):
            n['postage_stamp'].setValue(is_postage)
            result = shuffle_rgba(n)
            self.assertEqual(len(result), 4)
            for i in result:
                self.assertIsInstance(i, nuke.Node)
                self.assertEqual(i.Class(), 'Shuffle')
                self.assertIn(i['in'].value(), 'rgba')
                self.assertIn(i['out'].value(), 'rgba')
                self.assertEqual(i['postage_stamp'].value(), is_postage)
                for k in rgba:
                    self.assertIn(i[k].value(), rgba)
                    self.assertIn(i[k].value(), i[rgba[0]].value())

    def test_use_relative_path(self):
        from edit import use_relative_path

        nuke.knob('root.project_directory', 'A:/test/')
        n = nuke.nodes.Read(file=b'A:/test/sc01/testfile测试.mov')
        use_relative_path(n)
        self.assertEqual(n['file'].value(), b'sc01/testfile测试.mov')

    def test_gizmo_to_group(self):
        from edit import gizmo_to_group

        for is_selected in (True, False):
            gizmo = nuke.nodes.CameraShake(selected=is_selected)
            name = gizmo.name()
            self.assertIsInstance(gizmo, nuke.Gizmo)
            result = gizmo_to_group(gizmo)
            self.assertIsInstance(result, nuke.Group)
            self.assertEqual(result.name(), name)
            self.assertEqual(result['selected'].value(), is_selected)

    def test_enable_later(self):
        from edit import mark_enable, marked_nodes
        for _ in xrange(20):
            nuke.nodes.Grade()
        nodes = nuke.allNodes()
        mark_enable(nodes)
        self.assertEqual(len(nodes), 20)
        marked_nodes().disable()
        for i in nodes:
            self.assert_(i['disable'].value())
        marked_nodes().enable()
        for i in nodes:
            self.assertFalse(i['disable'].value())

    def test_insert_node(self):
        from edit import insert_node

        def _random_node():
            return random.choice(nuke.allNodes())

        nuke.nodes.NoOp()
        for _ in xrange(20):
            nuke.nodes.Grade(inputs=[_random_node(), _random_node()])
            target = _random_node()
            target_dependent = target.dependent()
            state = [(i, j)
                     for i in target_dependent
                     for j in xrange(i.inputs())
                     if i.input(j) is target]

            n = nuke.nodes.Grade()
            insert_node(n, target)
            self.assertIs(n.input(0), target)
            for i, j in state:
                self.assertIs(i.input(j), n)

    def test_copy_layer(self):
        from edit import copy_layer
        rgba = nuke.nodes.Constant()
        depth = nuke.nodes.Constant(
            channels='depth'
        )

        # Base case.
        result = copy_layer(depth, rgba)
        self.assertIsInstance(result, nuke.Node)
        self.assertEqual(result.Class(), 'Merge2')
        self.assertEqual(nuke.layers(result),
                         [b'rgb', b'rgba', b'alpha', b'depth'])

        # Self copy (shuffle).
        result = copy_layer(depth, depth, 'depth', 'rgba')
        self.assertIsInstance(result, nuke.Node)
        self.assertEqual(result.Class(), 'Shuffle')
        self.assertEqual(nuke.layers(result),
                         [b'rgb', b'rgba', b'alpha', b'depth'])

        # Skip no effect.
        result = copy_layer(rgba, rgba)
        self.assertIs(result, rgba)

        # Take rgba if no such layer in input1.
        result = copy_layer(rgba, rgba, 'depth')
        self.assertEqual(nuke.layers(result),
                         [b'rgb', b'rgba', b'alpha', b'depth'])

        # Raise ValueError if no such layer and no rgba in input1.
        self.assertRaises(ValueError, copy_layer, rgba, depth, 'rgba')

    def test_set_knobs(self):
        from edit import set_knobs

        n = nuke.nodes.Grade()
        set_knobs(n, white=8, black=9, hahaha='asd')
        self.assertEqual(n['white'].value(), 8)
        self.assertEqual(n['black'].value(), 9)

    def test_transfer_flags(self):
        from edit import transfer_flags

        all_flags = [pow(2, n) for n in range(31)]
        src = nuke.Int_Knob('src')
        dst = nuke.Int_Knob('dst')
        for i in all_flags:
            if random.randint(0, 1):
                src.setFlag(i)
            else:
                src.clearFlag(i)

        transfer_flags(src, dst)
        for i in all_flags:
            self.assertEqual(src.getFlag(i), dst.getFlag(i))

    def test_all_flags(self):
        from edit import all_flags

        print(all_flags())

    def tearDown(self):
        nuke.scriptClear(True)


if __name__ == '__main__':
    main()
