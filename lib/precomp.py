# -*- coding=UTF-8 -*-
"""Comp multi pass to beauty."""
import os
import json
import re
import logging

import nuke

from wlf.path import get_layer
from edit import add_layer, copy_layer, undoable_func
from orgnize import autoplace

__version__ = '0.3.17'
LOGGER = logging.getLogger('com.wlf.precomp')


@undoable_func('Redshift预合成')
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

        # Record node for every source layer.
        self.source = {}
        for n in nodes:
            layer = get_layer(
                nuke.filename(n), layers=self._config['layers'])
            n['label'].setValue(
                '\n'.join([n['label'].value(), self.l10n(layer)]).strip())
            if layer:
                self.source[layer] = n
            else:
                self.source['beauty'] = n
        if len(self.source) == 1:
            n = sorted(nodes,
                       key=lambda n: (len(nuke.layers(n)),
                                      len(nuke.filename(n)) * -1),
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
        self.last_node = nuke.nodes.Remove(
            inputs=[self.last_node], channels='rgb')
        for layer in self._config.get('plus'):
            self.plus(layer)

        autoplace(self.last_node, recursive=True, undoable=False)

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
            kwargs = {'inputs': [self.last_node],
                      'in': layer,
                      'label': u'修改日期: [metadata input/mtime]\n{}'.format(self.l10n(layer))}
            try:
                kwargs['postage_stamp'] = self.last_node['postage_stamp'].value()
            except NameError:
                pass
            ret = nuke.nodes.Shuffle(
                **kwargs)
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
                n = nuke.nodes.Merge2(**kwargs)
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
            label=self.l10n(layer),
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
