# -*- coding=UTF-8 -*-
# This typing file was generated by typing_from_help.py
"""
comp.precomp - Comp multi pass to beauty.
"""

import six
import typing


class Precomp:
    """
    A sequence of merge or copy.
    """

    def __init__(self, nodes, renderer=None, async_=True):
        """
        """
        ...

    def check(self):
        """
        Check if has all necessary layer.
        """
        ...

    def copy(self, layer, output=None):
        """
        Copy a layer to last.
        """
        ...

    def layers(self):
        """
        Return layers in self.last_node.
        """
        ...

    def node(self, layer):
        """
        Return a node that should be treat as @layer.
        """
        ...

    def plus(self, layer):
        """
        Plus a layer to last rgba.
        """
        ...

    ...


PrecompSwitch = __PrecompSwitch


class RendererConfig:
    def __init__(self):
        """
        """
        self.name: six.text_type = ...
        self.layers: typing.Set[six.text_type] = ...
        self.combine: typing.Dict[six.text_type, typing.List[six.text_type]] = ...
        self.combineMode: typing.Dict[six.text_type, six.text_type] = ...
        self.translate: typing.Dict[six.text_type, six.text_type] = ...
        self.copy: typing.List[six.text_type] = ...
        self.rename: typing.Dict[six.text_type, six.text_type] = ...
        self.plus: typing.List[six.text_type] = ...
        ...

    def fromJSON(self, data: typing.Dict[six.text_type, typing.Any]) -> RendererConfig:
        """
        load data from json.

        Args:
            data (Dict[str, Any]): Parsed json data.

        Returns:
            self: for method chaining.
        """
        ...

    def l10n(self, value: six.text_type) -> six.text_type:
        """
        Return translated value.
        """
        ...

    ...


class __PrecompSwitch:
    """
    Modified switch node for precomp.
    """

    @classmethod
    def get_which(cls, node):
        """
        Return auto input choice for @node.
        """
        ...

    @classmethod
    def hash(cls, node):
        """
        Node hash result of @node up to upstream start.
        """
        ...

    @classmethod
    def init(cls, node):
        """
        Add necessary knobs.
        """
        ...


    ...


def detect_renderer(layers: typing.List[six.binary_type]) -> RendererConfig:
    """
    """
    ...


def load_renderer_config():
    """
    """
    ...


LOGGER: ...
"""
<logging.Logger object>
"""


RENDERER_REGISTRY: typing.Dict[str, RendererConfig]
"""
{u'arnold': <comp.precomp.RendererConfig instance>...
"""

__all__: ...
"""
['Dict', 'LOGGER', 'List', 'Optional', 'Precomp', 'PrecompSw...
"""
