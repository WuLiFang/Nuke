# -*- coding=UTF-8 -*-
"""Comp multi pass to beauty."""
import os
import json
import re

import nuke

from wlf.files import get_layer
from wlf.edit import add_layer, copy_layer
from wlf.orgnize import autoplace

__version__ = '0.3.0'


def redshift(nodes):
    """Precomp reshift footages.  """

    return Precomp(nodes, renderer='redshift')


class Precomp(object):
    """A sequence of merge or copy.  """
    last_node = None

    def __init__(self, nodes, renderer='redshift'):
        config_file = os.path.join(
            __file__, '../precomp.{}.json'.format(renderer))
        with open(config_file) as f:
            self._config = json.load(f)

        if len(nodes) == 1:
            n = nodes if isinstance(nodes, nuke.Node) else nodes[0]
            layers = nuke.layers(n)
            self._source = {layer: None
                            for layer in layers if layer in self._config['layers']}
            self.last_node = n
        else:
            self._source = {}
            for n in nodes:
                layer = get_layer(nuke.filename(n))
                if layer:
                    self._source[layer] = n

        base_layer = self._config['layers'][0]
        self.last_node = self.node(base_layer)
        if not self.last_node:
            raise ValueError('缺少{}'.format(base_layer))

        if base_layer not in self.layers():
            self.last_node = nuke.nodes.Shuffle(
                inputs=[self.last_node], out=base_layer)

        for layer in self._config.get('copy'):
            for i in self.source.keys():
                if re.match('(?i)^{}\\d*$'.format(layer), i):
                    self.copy(i)
        for layer, output in dict(self._config.get('rename')).items():
            self.copy(layer, output)
        for layer in self._config.get('plus'):
            self.plus(layer)

        autoplace(self.last_node, recursive=True)

    @property
    def source(self):
        """A layer-node dictionary.  """
        return self._source

    @property
    def _combine_dict(self):
        return dict(self._config.get('combine'))

    def check(self):
        """Check if has all necessary layer.  """
        pass

    def layers(self):
        """Return layers in self.last_node. """
        if not self.last_node:
            return []
        return nuke.layers(self.last_node)

    def node(self, layer):
        """Return a node that should be treat as @layer.  """
        add_layer(layer)
        ret = self.source.get(layer)
        if layer in self.layers():
            ret = self.last_node
        elif layer in self._combine_dict.keys():
            pair = self._combine_dict[layer]
            if self.source.get(pair[0])\
                    and self.source.get(pair[1]):
                input0, input1 = self.node(pair[0]), self.node(pair[1])
                n = nuke.nodes.Merge2(
                    inputs=[input0, input1],
                    Achannels=pair[1] if pair[1] in nuke.layers(
                        input1) else 'rgb',
                    operation='multiply', output='rgb', label=layer)
                self.source[layer] = n
                ret = n
        return ret

    def plus(self, layer):
        """Plus a layer to last.  """
        input1 = self.node(layer)
        input1 = nuke.nodes.ColorCorrect(inputs=[input1])
        input1 = nuke.nodes.Shuffle(inputs=[input1], out=layer)
        self.last_node = nuke.nodes.Merge2(
            inputs=[self.last_node, input1], operation='plus',
            Achannels=layer if layer in nuke.layers(input1) else 'rgb',
            output='rgb',
            also_merge=layer if layer not in self.layers() else 'none',
            label=layer)

    def multiply(self, layer):
        """Plus a layer to last.  """
        pass

    def copy(self, layer, output=None):
        """Copy a layer to last.  """
        if layer not in self.layers() and self.source.get(layer):
            self.last_node = copy_layer(
                self.last_node, self.node(layer), layer=layer, output=output)
