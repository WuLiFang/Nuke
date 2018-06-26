# -*- coding=UTF-8 -*-
"""Comp multi pass to beauty."""
from __future__ import absolute_import, unicode_literals

import inspect
import json
import logging
import re
import sys

import nuke

import filetools
from edit import add_layer, copy_layer, replace_node
from nuketools import undoable_func, utf8, utf8_dict
from orgnize import autoplace
from wlf.codectools import get_unicode as u, get_encoded as e
from wlf.path import PurePath

LOGGER = logging.getLogger('com.wlf.precomp')


class __PrecompSwitch(object):
    """Modified switch node for precomp.  """

    knob_name = 'raw_hash'

    @classmethod
    def init(cls, node):
        """Add necessary knobs.  """

        assert isinstance(
            node, nuke.Node), 'Expect a node, got: {}'.format(node)

        knob_name = cls.knob_name
        knobs = node.knobs()
        if knob_name not in knobs:
            n = node.input(1)
            raw_hash = cls.hash(n)
            k = nuke.Int_Knob(knob_name)
            k.setValue(raw_hash)
            node.addKnob(k)
        else:
            k = knobs[knob_name]
        k.setFlag(nuke.READ_ONLY)
        return node

    @classmethod
    def hash(cls, node):
        """Node hash result of @node up to upstream start.  """

        assert isinstance(
            node, nuke.Node), 'Expect a node, got: {}'.format(node)

        def _hash(n):
            assert isinstance(n, nuke.Node)
            ret = n.writeKnobs(nuke.WRITE_ALL | nuke.WRITE_NON_DEFAULT_ONLY)
            assert isinstance(ret, (str, unicode))
            ret = ret.split()
            assert isinstance(ret, list)
            for knob in ('xpos', 'ypos', 'selected',
                         'name', 'gl_color', 'tile_color'
                         'label', 'note_font', 'note_font_size', 'note_font_color',
                         'hide_input', 'cached', 'cached', 'dope_sheet', 'bookmark',
                         'postage_stamp', 'postage_stamp_frame'):
                if knob in ret:
                    ret.remove(knob)
            ret = hash(tuple(ret))
            return ret

        def _get_upstream(nodes, flags=nuke.INPUTS | nuke.HIDDEN_INPUTS):
            ret = set()
            if isinstance(nodes, nuke.Node):
                nodes = [nodes]

            nodes = tuple(nodes)
            while nodes:
                deps = nuke.dependencies(nodes, flags)
                nodes = [n for n in deps
                         if n not in ret
                         and n not in nodes
                         and n.Class() in ('Merge2', 'Shuffle')]
                ret.update(set(deps))
            return ret

        nodes = _get_upstream(node)
        ret = _hash(node)

        for n in nodes:
            ret += _hash(n)
        ret = hash(ret)

        return ret

    @classmethod
    def get_which(cls, node):
        """Return auto input choice for @node.  """

        assert isinstance(node, nuke.Node)\
            and node.Class() == 'Switch',\
            'Expect a switch node, got: {}'.format(node)

        n = node.input(1)
        if not n:
            ret = False
        elif cls.knob_name not in node.knobs():
            ret = True
        else:
            ret = node[cls.knob_name].value() != cls.hash(n)

        node['tile_color'].setValue(0xFFFFFFFF if ret else 0x000000FF)
        return ret


PrecompSwitch = __PrecompSwitch


class Precomp(object):
    """A sequence of merge or copy.  """

    last_node = None

    def __init__(self, nodes, renderer='redshift', async_=True):
        assert nodes, 'Can not precomp without node.'

        def _get_filename(n):
            return n.metadata('input/filename') or nuke.filename(n) or ''

        config_file = filetools.path(
            'data', 'precomp.{}.json'.format(renderer))
        with open(e(config_file)) as f:
            self._config = json.load(f)
        self._combine_dict = dict(self._config.get('combine'))
        self._translate_dict = dict(self._config.get('translate'))
        if isinstance(nodes, nuke.Node):
            nodes = [nodes]
        elif len(nodes) > 1:
            nodes = list(n for n in nodes if n.Class() == 'Read')

        # Record node for every source layer.
        self.source = {}
        for n in nodes:
            path = PurePath(_get_filename(n))
            path.layers = self._config['layers']
            layer = path.layer
            _layer = self.l10n(layer)
            _label = u(n['label'].value())
            if _layer not in _label:
                n['label'].setValue('{}\n{}'.format(
                    _label, _layer).strip().encode('utf-8'))
            if layer:
                self.source[layer] = n
            else:
                self.source['beauty'] = n
        if len(self.source) == 1:
            n = sorted(nodes,
                       key=lambda n: (len(nuke.layers(n)),
                                      len(_get_filename(n)) * -1),
                       reverse=True)[0]
            layers = nuke.layers(n)
            LOGGER.debug(
                'Precomp single node that has this layers:\n%s', layers)
            self.source = {layer: True
                           for layer in layers if layer in self._config['layers']}
            self.source['beauty'] = n
            self.last_node = n
        LOGGER.debug('Source layers:\n%s', self.source.keys())

        self.last_node = self.node('beauty')
        for layer in self._config.get('copy'):
            for i in self.source.keys():
                if re.match('(?i)^{}\\d*$'.format(layer), i):
                    self.copy(i)
        for layer, output in dict(self._config.get('rename')).items():
            self.copy(layer, output)

        # Plus nodes.
        dot_node = nuke.nodes.Dot(inputs=(self.last_node,))
        remove_node = nuke.nodes.Remove(
            inputs=(dot_node,), channels='rgb')
        self.last_node = remove_node
        for layer in self._config.get('plus'):
            self.plus(layer)

        # Precomp Switch.
        kwargs = {'which':
                  '{{[python {__PrecompSwitch.get_which(nuke.thisNode())}]}}',
                  'inputs': [dot_node, self.last_node],
                  'label': '预合成自动开关',
                  'onCreate': inspect.getsource(PrecompSwitch) + """
__PrecompSwitch.init(nuke.thisNode())"""}
        setattr(sys.modules['__main__'], '__PrecompSwitch', PrecompSwitch)
        if self.last_node is remove_node:
            kwargs['disable'] = True
        self.last_node = PrecompSwitch.init(
            nuke.nodes.Switch(**utf8_dict(kwargs)))

        replace_node(dot_node.input(0), self.last_node)

        autoplace(self.last_node, recursive=True,
                  undoable=False, async_=async_)

    def check(self):
        """Check if has all necessary layer.  """
        pass

    def layers(self):
        """Return layers in self.last_node. """

        if not self.last_node:
            return []
        return nuke.layers(self.last_node)

    def l10n(self, value):
        """Return translated value.  """

        if not value:
            return ''
        for pat in self._translate_dict:
            if re.match(pat, value):
                return re.sub(pat, self._translate_dict[pat], value)
        return u(value)

    def node(self, layer):
        """Return a node that should be treat as @layer.  """

        add_layer(layer)
        ret = self.source.get(layer)
        if layer in self.layers():
            kwargs = {'inputs': (self.last_node,),
                      'in': layer,
                      'label': '修改日期: [metadata input/mtime]\n{}'.format(self.l10n(layer))}
            try:
                kwargs['postage_stamp'] = self.last_node['postage_stamp'].value()
            except NameError:
                pass
            ret = nuke.nodes.Shuffle(**utf8(kwargs))
        elif layer in self._combine_dict.keys():
            pair = self._combine_dict[layer]
            if self.source.get(pair[0])\
                    and self.source.get(pair[1]):
                LOGGER.debug('Combine for layer: %s, %s -> %s',
                             pair[0], pair[1], layer)
                input0, input1 = self.node(pair[0]), self.node(pair[1])
                kwargs = {'inputs': [input0, input1],
                          'operation': 'multiply',
                          'output': 'rgb',
                          'label': self.l10n(layer)}
                try:
                    kwargs['postage_stamp'] = (input0['postage_stamp'].value()
                                               and input1['postage_stamp'].value())
                except NameError:
                    pass
                n = nuke.nodes.Merge2(**utf8_dict(kwargs))
                self.source[layer] = n
                ret = n
            else:
                LOGGER.debug('Source not enough: %s', self.source.keys())
        if not ret:
            LOGGER.debug('Can not get node for layer:%s', layer)
        return ret

    def plus(self, layer):
        """Plus a layer to last rgba.  """

        input1 = self.node(layer)
        if not input1:
            return
        LOGGER.debug('Plus layer to last:%s', layer)
        if not self.last_node:
            self.last_node = nuke.nodes.Constant()

        if layer not in self.layers():
            input1 = nuke.nodes.Shuffle(inputs=[input1], out=layer)
        self.last_node = nuke.nodes.Merge2(
            inputs=[self.last_node, input1], operation='plus',
            also_merge=layer if layer not in self.layers() else 'none',
            label=utf8(self.l10n(layer)),
            output='rgb')

    def copy(self, layer, output=None):
        """Copy a layer to last.  """

        if not self.last_node:
            self.last_node = self.node(layer)
        elif layer not in self.layers() and self.source.get(layer):
            LOGGER.debug('Copy layer to last:%s -> %s', layer, output or layer)
            self.last_node = copy_layer(
                self.last_node, self.node(layer), layer=layer, output=output)

    def multiply(self, layer):
        """Plus a layer to last.  """
        pass

    @classmethod
    @undoable_func('Redshift预合成')
    def redshift(cls, nodes, **kwargs):
        """Precomp reshift footages.  """

        return cls(nodes, renderer='redshift', **kwargs).last_node
