# -*- coding=UTF-8 -*-
"""Patch nukescript precomp functions.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

import nuke
import six

from wlf.codectools import get_unicode as u
from wlf.path import PurePath

from .core import BasePatch

LOGGER = logging.getLogger(__name__)


class PatchPrecompDialog(BasePatch):
    """Enhance precomp creation """
    target = 'nukescripts.PrecompOptionsDialog.__init__'

    @classmethod
    def func(cls, *args, **kwargs):
        self = args[0]
        cls.orig(*args, **kwargs)

        self.precompName = nuke.String_Knob(
            'precomp_name'.encode('utf-8'),
            '预合成名称'.encode('utf-8'),
            'precomp1'.encode('utf-8'))
        self.addKnob(self.precompName)

        self.scriptPath.setLabel('脚本路径'.encode('utf-8'))
        self.renderPath.setLabel('渲染路径'.encode('utf-8'))
        self.channels.setLabel('输出通道'.encode('utf-8'))
        self.origNodes.setLabel('原节点'.encode('utf-8'))

        _knob_changed(self, self.precompName)
        nuke.addKnobChanged(
            lambda self: _knob_changed(self, nuke.thisKnob()),
            args=self,
            nodeClass='PanelNode',
            node=self._PythonPanel__node)  # pylint: disable=protected-access


def _on_precomp_name_changed(self, knob):
    rootpath = PurePath(u(nuke.value('root.name')))
    name = u(knob.value()) or 'precomp1'
    script_path = (rootpath.parent /
                   ''.join([rootpath.stem]
                           + ['.{}'.format(name)]
                           + rootpath.suffixes)).as_posix()
    render_path = 'precomp/{0}/{0}.%04d.exr'.format(
        ''.join([rootpath.stem]
                + ['.{}'.format(name)]
                + [i for i in rootpath.suffixes if i != '.nk']))
    self.scriptPath.setValue(script_path.encode('utf-8'))
    self.renderPath.setValue(render_path.encode('utf-8'))


def _knob_changed(self, knob):
    {
        self.precompName: _on_precomp_name_changed,
    }.get(knob, lambda *_: None)(self, knob)
    options = {name: k.value() for name, k in self.knobs().items()}
    options = {k: u(v) if isinstance(v, six.binary_type) else v
               for k, v in options.items()}
    PatchPrecompSelected.current_options = options
    assert PatchPrecompSelected.current_options


class PatchPrecompSelected(BasePatch):
    """Enhance precomp creation.  """

    target = 'nukescripts.precomp_selected'
    current_options = None
    current_precomp_node = None

    @classmethod
    def func(cls, *args, **kwargs):
        ret = cls.orig(*args, **kwargs)

        if ret is None or not cls.current_options:
            return ret

        group = nuke.nodes.Group()
        with group:
            nuke.scriptReadFile(cls.current_options['script'].encode('utf-8'))
            write_nodes = nuke.allNodes('Write')
            assert write_nodes
            if len(write_nodes) != 1:
                nuke.message('注意: 预合成中发现了多个输出节点, 可能导致渲染出错'.encode('utf-8'))
            name = '_'.join(
                i for i in ('Write',
                            cls.current_options['precomp_name'].upper(),
                            '1') if i)
            for n in write_nodes:
                n.setName(name.encode('utf-8'))
                # Disable exr hash check.
                n['metadata'].setValue('no metadata'.encode('utf-8'))
            nuke.tcl(b"export_as_precomp",
                     cls.current_options['script'].encode('utf-8'))
            if cls.current_precomp_node:
                cls.current_precomp_node.reload()
            else:
                LOGGER.warning(
                    'Not found precomp node after `precomp_selected`')

        nuke.delete(group)
        cls.current_options = None
        cls.current_precomp_node = None

        return ret


def enable():
    """Enable patch.  """

    PatchPrecompDialog.enable()
    PatchPrecompSelected.enable()


def disable():
    """Disable patch.  """

    PatchPrecompDialog.disable()
    PatchPrecompSelected.disable()
