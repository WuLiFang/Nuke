# -*- coding=UTF-8 -*-
"""Comp multi pass to beauty."""
import os
import json
import re

import nuke

from wlf.path import get_layer
from edit import add_layer, copy_layer
from orgnize import autoplace

__version__ = '0.3.14'


def redshift(nodes):
    """Precomp reshift footages.  """
    return Precomp(nodes, renderer='redshift').last_node


class Precomp(object):
    """A sequence of merge or copy.  """
    last_node = None

    def __init__(self, nodes, renderer='redshift'):
        assert nodes, 'Can not precomp without node.'

        config_file = os.path.join(
            __file__, '../wlf/precomp.{}.json'.format(renderer))
        with open(config_file) as f:
            self._config = json.load(f)
        self._combine_dict = dict(self._config.get('combine'))
        self._translate_dict = dict(self._config.get('translate'))
        if isinstance(nodes, nuke.Node):
            nodes = [nodes]
        nodes = list(n for n in nodes if n.Class() == 'Read')

        if len(nodes) == 1:
            n = nodes[0]
            layers = nuke.layers(n)
            self._source = {layer: True
                            for layer in layers if layer in self._config['layers']}
            self.source['beauty'] = n
            self.last_node = n
        else:
            self._source = {}
            for n in nodes:
                layer = get_layer(
                    nuke.filename(n), layers=self._config['layers'])
                n['label'].setValue(
                    '\n'.join([n['label'].value(), self.l10n(layer)]).strip())
                if layer:
                    self._source[layer] = n
                else:
                    self._source['beauty'] = n

        self.last_node = self.node('beauty')
        for layer in self._config.get('copy'):
            for i in self.source.keys():
                if re.match('(?i)^{}\\d*$'.format(layer), i):
                    self.copy(i)
        for layer, output in dict(self._config.get('rename')).items():
            self.copy(layer, output)
        self.last_node = nuke.nodes.Remove(
            inputs=[self.last_node], channels='rgb')
        for layer in self._config.get('plus'):
            self.plus(layer)

        autoplace(self.last_node, recursive=True)

    @property
    def source(self):
        """A layer-node dictionary.  """
        return self._source

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
        return value

    def node(self, layer):
        """Return a node that should be treat as @layer.  """
        add_layer(layer)
        ret = self.source.get(layer)
        if layer in self.layers():
            _kwargs = {'in': layer}
            ret = nuke.nodes.Shuffle(
                inputs=[self.last_node],
                label=u'修改日期: [metadata input/mtime]\n{}'.format(
                    self.l10n(layer)),
                postage_stamp=self.last_node.Class() != 'Read', **_kwargs)
        elif layer in self._combine_dict.keys():
            pair = self._combine_dict[layer]
            if self.source.get(pair[0])\
                    and self.source.get(pair[1]):
                input0, input1 = self.node(pair[0]), self.node(pair[1])
                n = nuke.nodes.Merge2(
                    inputs=[input0, input1],
                    operation='multiply', output='rgb',
                    label=self.l10n(layer),
                    postage_stamp=True)
                self.source[layer] = n
                ret = n
        return ret

    def plus(self, layer):
        """Plus a layer to last rgba.  """

        input1 = self.node(layer)
        if not input1:
            return
        if not self.last_node:
            self.last_node = nuke.nodes.Constant()

        if layer not in self.layers():
            input1 = nuke.nodes.Shuffle(inputs=[input1], out=layer)
        self.last_node = nuke.nodes.Merge2(
            inputs=[self.last_node, input1], operation='plus',
            also_merge=layer if layer not in self.layers() else 'none',
            label=self.l10n(layer),
            output='rgb')

    def copy(self, layer, output=None):
        """Copy a layer to last.  """

        if not self.last_node:
            self.last_node = self.node(layer)
        elif layer not in self.layers() and self.source.get(layer):
            self.last_node = copy_layer(
                self.last_node, self.node(layer), layer=layer, output=output)

    def multiply(self, layer):
        """Plus a layer to last.  """
        pass
