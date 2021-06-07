# -*- coding=UTF-8 -*-
"""Test edit module.  """

from __future__ import absolute_import, print_function, unicode_literals

import random
import sys
from unittest import TestCase, main
import six
import nuke

import cast_unknown as cast
import edit


class EditTestCase(TestCase):
    def setUp(self):
        nuke.scriptClear(True)

    def test_add_channel(self):
        from edit import add_channel

        add_channel("test.channel")
        self.assertIn("test.channel", nuke.Root().channels())
        add_channel("test.channel2")
        self.assertIn("test.channel2", nuke.Root().channels())
        self.assertRaises(ValueError, add_channel, "test.channel3中文")
        self.assertRaises(ValueError, add_channel, cast.binary("test.channel4中文"))
        add_channel("test channel5")
        self.assertIn("other.test channel5", nuke.Root().channels())
        self.assertRaises(ValueError, add_channel, "test.channel6.test")

    def test_add_layer(self):
        from edit import add_layer

        self.assertNotIn("test", nuke.layers())
        _ = add_layer("test")
        self.assertIn("test", nuke.layers())
        for i in ("test.red", "test.green", "test.blue", "test.alpha"):
            self.assertIn(i, nuke.channels())

    def test_doctest(self):
        from doctest import testmod
        import edit

        self.assertFalse(testmod(edit).failed, "Doctest failed")

    def test_named_copy(self):
        from edit import named_copy

        # Normal case.
        n = nuke.nodes.Constant()
        n = nuke.nodes.AddChannels(
            inputs=[n],
            channels="mask.a",
            channels2="depth.Z",
            channels3="forward.v",
        )
        names_dict = {
            "r": "test1",
            "green": "test2",
            "rgba.blue": "test3",
            "rgba.alpha": "test4",
            "depth.Z": "test5 test",
            "forward.v": "test6测试",
            "mask.a": "test7.test",
        }
        n = named_copy(n, names_dict)
        self.assertIsInstance(n, nuke.Node)
        self.assertEqual(n.Class(), "Copy")
        self.assertEqual(len(nuke.allNodes(b"Copy")), ((len(names_dict) - 1) / 4) + 1)

        self.assertEqual(
            n.channels(),
            [
                b"rgba.red",
                b"rgba.green",
                b"rgba.blue",
                b"rgba.alpha",
                b"depth.Z",
                b"forward.v",
                b"mask.a",
                # Ordered according input channels.
                b"mask_extra.test5_test",
                b"mask_extra.test6??",
                b"test7.test",
                b"mask_extra.test1",
                b"mask_extra.test2",
                b"mask_extra.test3",
                b"mask_extra.test4",
            ],
        )
        # 　Empty names_dict.
        last = named_copy(n, {})
        self.assertIs(n, last)

    def test_replace_node(self):
        from edit import replace_node

        const = nuke.nodes.Constant()
        for _ in six.moves.range(20):
            _ = nuke.nodes.Grade(inputs=[const])
        nodes = nuke.allNodes(b"Grade")
        self.assertEqual(len(nodes), 20)
        noop = nuke.nodes.NoOp()
        replace_node(const, noop)
        for i in nodes:
            self.assertIs(i.input(0), noop)

        self.assertRaises(TypeError, replace_node, noop, 1)
        self.assertRaises(AttributeError, replace_node, 1, noop)

    def test_get_min_max(self):
        from edit import get_min_max

        for _ in six.moves.range(5):
            color = random.random()
            n = nuke.nodes.AddChannels(channels="depth.Z", color=color)
            result = get_min_max(n, "depth.Z")
            self.assertAlmostEqual(result[0], color)
            self.assertAlmostEqual(result[1], color)

    def test_random_glcolor(self):
        from edit import set_random_glcolor

        n = nuke.nodes.NoOp()
        self.assertFalse(n[b"gl_color"].value())
        for _ in six.moves.range(10):
            set_random_glcolor(n)
            self.assert_(n[b"gl_color"].value() != 0)

    def test_clear_selection(self):
        from edit import clear_selection

        for _ in six.moves.range(20):
            _ = nuke.nodes.NoOp(selected=True)
        self.assertEqual(len(nuke.selectedNodes()), 20)
        clear_selection()
        self.assertFalse(nuke.selectedNodes())

    def test_split_layers(self):
        from edit import split_layers

        n = nuke.nodes.Constant()
        _ = nuke.Layer(
            b"test", [b"test.red", b"test.green", b"test.blue", b"test.alpha"]
        )
        _ = nuke.Layer(b"test2", [b"test2.red", b"test2.green", b"test2.blue"])
        _ = nuke.Layer(b"test3", [b"test3.u", b"test3.v"])
        _ = nuke.Layer(b"test4", [b"test4.Z"])
        layers = ("test", "test2", "test3", "test4")

        for i in layers:
            n = nuke.nodes.AddChannels(inputs=[n], channels=i)
        for is_postage in (True, False):
            _ = n[b"postage_stamp"].setValue(is_postage)
            result = split_layers(n)
            self.assertEqual(len(result), 4)
            for i in result:
                self.assertIsInstance(i, nuke.Node)
                assert isinstance(i, nuke.Node)
                self.assertEqual(i.Class(), "Shuffle")
                self.assertIn(i[b"in"].value(), layers)
                self.assertEqual(i[b"postage_stamp"].value(), is_postage)

    def test_shuffle_rgba(self):
        from edit import shuffle_rgba

        rgba = ("red", "green", "blue", "alpha")

        n = nuke.nodes.Constant()
        for is_postage in (True, False):
            _ = n[b"postage_stamp"].setValue(is_postage)
            result = shuffle_rgba(n)
            self.assertEqual(len(result), 4)
            for i in result:
                self.assertIsInstance(i, nuke.Node)
                assert isinstance(i, nuke.Node)
                self.assertEqual(i.Class(), "Shuffle")
                self.assertIn(i[b"in"].value(), "rgba")
                self.assertIn(i[b"out"].value(), "rgba")
                self.assertEqual(i[b"postage_stamp"].value(), is_postage)
                for k in rgba:
                    k = cast.binary(k)
                    self.assertIn(i[k].value(), rgba)
                    self.assertIn(i[k].value(), i[cast.binary(rgba[0])].value())

    def test_use_relative_path(self):
        from edit import use_relative_path

        root = "A:/test/" if sys.platform == "win32" else "/tmp/test"
        nuke.knob(b"root.project_directory", cast.binary(root))
        n = nuke.nodes.Read(file=(root + "/sc01/testfile测试.mov").encode("utf-8"))
        use_relative_path(n)
        self.assertEqual(n[b"file"].value(), "sc01/testfile测试.mov".encode("utf-8"))

    def test_gizmo_to_group(self):
        from edit import gizmo_to_group

        for is_selected in (True, False):
            gizmo = nuke.nodes.CameraShake(selected=is_selected)
            name = gizmo.name()
            self.assertIsInstance(gizmo, nuke.Gizmo)
            result = gizmo_to_group(gizmo)
            self.assertIsInstance(result, nuke.Group)
            self.assertEqual(result.name(), name)
            self.assertEqual(result[b"selected"].value(), is_selected)

    def test_enable_later(self):
        from enable_later import mark_enable, marked_nodes

        for _ in six.moves.range(20):
            _ = nuke.nodes.Grade()
        nodes = nuke.allNodes()
        self.assertEqual(len(nodes), 20)
        mark_enable(nodes)
        marked = marked_nodes()
        self.assertEqual(len(marked), 20)
        marked.disable()
        for i in nodes:
            self.assert_(i[b"disable"].value())
        marked.enable()
        for i in nodes:
            self.assertFalse(i[b"disable"].value())

    def test_insert_node(self):
        from edit import insert_node

        def _random_node():
            return random.choice(nuke.allNodes())

        _ = nuke.nodes.NoOp()
        for _ in six.moves.range(20):
            _ = nuke.nodes.Grade(inputs=[_random_node(), _random_node()])
            target = _random_node()
            target_dependent = target.dependent()
            state = [
                (i, j)
                for i in target_dependent
                for j in six.moves.range(i.inputs())
                if i.input(j) is target
            ]

            n = nuke.nodes.Grade()
            insert_node(n, target)
            self.assertIs(n.input(0), target)
            for i, j in state:
                self.assertIs(i.input(j), n)

    def test_copy_layer(self):
        from edit import copy_layer

        rgba = nuke.nodes.Constant()
        depth = nuke.nodes.Constant(channels="depth")

        # Base case.
        result = copy_layer(depth, rgba)
        self.assertIsInstance(result, nuke.Node)
        self.assertEqual(result.Class(), "Merge2")
        self.assertEqual(nuke.layers(result), [b"rgb", b"rgba", b"alpha", b"depth"])

        # Self copy (shuffle).
        result = copy_layer(depth, depth, "depth", "rgba")
        self.assertIsInstance(result, nuke.Node)
        self.assertEqual(result.Class(), "Shuffle")
        self.assertEqual(nuke.layers(result), [b"rgb", b"rgba", b"alpha", b"depth"])

        # Skip no effect.
        result = copy_layer(rgba, rgba)
        self.assertIs(result, rgba)

        # Take rgba if no such layer in input1.
        result = copy_layer(rgba, rgba, "depth")
        self.assertEqual(nuke.layers(result), [b"rgb", b"rgba", b"alpha", b"depth"])

        # Raise ValueError if no such layer and no rgba in input1.
        self.assertRaises(ValueError, copy_layer, rgba, depth, "rgba")

    def test_set_knobs(self):
        from edit import set_knobs

        n = nuke.nodes.Grade()
        set_knobs(n, white=8, black=9, hahaha="asd")
        self.assertEqual(n[b"white"].value(), 8)
        self.assertEqual(n[b"black"].value(), 9)

    def test_transfer_flags(self):
        from edit import transfer_flags

        all_flags = [pow(2, n) for n in range(31)]
        src = nuke.Int_Knob(b"src")
        dst = nuke.Int_Knob(b"dst")
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


def test_remove_duplicated_read():
    nuke.scriptClear(True)
    nodes = [
        nuke.nodes.Read(
            file=b"dummy file",
        )
        for _ in six.moves.range(10)
    ]
    downstream_nodes = [nuke.nodes.NoOp(inputs=[n]) for n in nodes]
    assert len(nuke.allNodes(b"Read")) == 10
    assert not nuke.allNodes(b"Dot")
    edit.remove_duplicated_read()
    assert len(nuke.allNodes(b"Read")) == 1
    assert len(nuke.allNodes(b"Dot")) == 9
    for n in downstream_nodes:
        assert n.input(0).Class() in ("Read", "Dot")


def test_glow_no_mask():
    nuke.scriptClear(True)
    mask_channel = "red"
    width_channel = "blue"
    temp_channel = "mask.a"
    n = nuke.nodes.Glow2(
        inputs=(None, nuke.nodes.Constant()),
        W=width_channel,
        maskChannelMask=mask_channel,
    )
    edit.best_practice.glow_no_mask(temp_channel)
    assert n[b"W"].value() == temp_channel
    assert n[b"mask"].value() == "none"
    assert n.input(1) is None
    n = n.input(0)
    assert n.Class() == "ChannelMerge"
    assert n[b"A"].value() == temp_channel
    assert n[b"operation"].value() == "in"
    assert n[b"B"].value() == width_channel
    n = n.input(0)
    assert n.Class() == "Copy"
    assert n[b"from0"].value() == mask_channel
    assert n[b"to0"].value() == temp_channel


def test_delete_unused_node():
    nuke.scriptClear(True)
    _ = [nuke.nodes.NoOp() for _ in six.moves.range(10)]
    n = nuke.nodes.NoOp(name=b"_test")
    assert len(nuke.allNodes()) == 11
    edit.delete_unused_nodes()
    assert nuke.allNodes() == [n]


if __name__ == "__main__":
    _ = main()
