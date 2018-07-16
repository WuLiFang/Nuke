# -*- coding: UTF-8 -*-
"""UI for edit operation."""

from __future__ import absolute_import, print_function, unicode_literals

import nuke

from edit import (CurrentViewer, named_copy, replace_node, set_knobs,
                  transfer_flags)
from nodeutil import is_node_deleted
from nuketools import undoable_func
from panels import PythonPanel
from wlf.progress import CancelledError, progress


class ChannelsRename(PythonPanel):
    """Dialog UI of channel_rename."""

    widget_id = 'com.wlf.channels_rename'

    def __init__(self, prefix=('PuzzleMatte', 'ID'), node=None):
        def _pannel_order(name):
            return (
                name.endswith('.alpha'),
                name.startswith(prefix),
                name.split('.')[0],
                name.endswith('.blue'),
                name.endswith('.green'),
                name.endswith('.red'),
            )

        def _stylize(text):
            ret = text
            repl = {'.red': '.<span style=\"color:#FF4444\">red</span>',
                    '.green':  '.<span style=\"color:#44FF44\">green</span>',
                    '.blue': '.<span style=\"color:#4444FF\">blue</span>'}
            for k, v in repl.iteritems():
                ret = ret.replace(k, v)
            return ret

        super(ChannelsRename, self).__init__(b'重命名通道', self.widget_id)

        viewer = CurrentViewer()
        n = node or nuke.selectedNode()
        self._channels = sorted((channel for channel in n.channels()
                                 if channel.startswith(prefix)),
                                key=_pannel_order) + ['rgba.alpha']
        self._node = n
        self._viewer = viewer

        nuke.Undo.disable()

        n = nuke.nodes.LayerContactSheet(inputs=[n], showLayerNames=1)
        self._layercontactsheet = n

        viewer.link(n)
        viewer.node['channels'].setValue('rgba')

        for channel in self._channels:
            self.addKnob(nuke.String_Knob(
                channel, _stylize(channel), ''))
            if channel.endswith('.blue'):
                self.addKnob(nuke.Text_Knob(''))
        self.addKnob(nuke.Text_Knob(''))
        k = nuke.Script_Knob('ok', 'OK')
        k.setFlag(nuke.STARTLINE)
        self.addKnob(k)
        k = nuke.Script_Knob('cancel', 'Cancel')
        self.addKnob(k)

        nuke.Undo.enable()

        self.add_callbacks()

    def add_callbacks(self):
        """Add nuke callbacks.  """

        nuke.removeOnDestroy(ChannelsRename.hide, args=(self))
        nuke.addOnUserCreate(ChannelsRename.hide, args=(self))

    def remove_callbacks(self):
        """Remove nuke callbacks.  """

        nuke.removeOnDestroy(ChannelsRename.hide, args=(self))
        nuke.removeOnUserCreate(ChannelsRename.hide, args=(self))

    def destroy(self):
        """Destroy the panel.  """

        if not is_node_deleted(self._layercontactsheet):
            nuke.Undo.disable()
            self._layercontactsheet['label'].setValue('[delete this]')
            nuke.Undo.enable()
        self.remove_callbacks()
        super(ChannelsRename, self).destroy()

    def knobChanged(self, knob):
        """Override. """

        if knob in (self['ok'], self['cancel']):
            self._viewer.recover()
            if knob is self['ok']:
                self.accept()
            else:
                self.reject()
            self.destroy()

    @undoable_func('重命名通道')
    def accept(self):
        """Execute named copy.  """

        n = named_copy(self._node,
                       {channel: self[channel].value()
                        for channel in self._channels})
        replace_node(self._node, n)


class MultiEdit(PythonPanel):
    """Edit multiple same class node at once.  """
    nodes = None
    widget_id = 'com.wlf.multiedit'

    def __init__(self, nodes=None):
        super(MultiEdit, self).__init__(b'多节点编辑', self.widget_id)

        nodes = nodes or nuke.selectedNodes()
        assert nodes, 'Nodes not given. '
        nodes = same_class_filter(nodes)
        self.nodes = nodes
        self._values = {}

        knobs = nodes[0].allKnobs()

        self.addKnob(nuke.Text_Knob('', b'以 {} 为模版'.format(nodes[0].name())))
        self.addKnob(nuke.Tab_Knob('', nodes[0].Class()))

        def _tab_knob():
            if label is None:
                new_k = nuke.Tab_Knob(name, label, nuke.TABENDGROUP)
            elif label.startswith('@b;'):
                new_k = nuke.Tab_Knob(name, label, nuke.TABBEGINGROUP)
            else:
                new_k = knob_class(name, label)
            return new_k

        for k in knobs:
            name = k.name()
            label = k.label() or None

            knob_class = getattr(nuke, type(k).__name__)

            if issubclass(knob_class, (nuke.Script_Knob, nuke.Obsolete_Knob)) \
                    or knob_class is nuke.Knob:
                continue
            elif issubclass(knob_class, nuke.Channel_Knob):
                new_k = nuke.Channel_Knob(name, label, k.depth())
            elif issubclass(knob_class, nuke.Enumeration_Knob):
                enums = [k.enumName(i) for i in range(k.numValues())]
                new_k = knob_class(name, label, enums)
            elif issubclass(knob_class, nuke.Tab_Knob):
                new_k = _tab_knob()
            elif issubclass(knob_class, nuke.Array_Knob):
                new_k = knob_class(name, label)
                new_k.setRange(k.min(), k.max())
            else:
                # print(knob_class, name, label)
                new_k = knob_class(name, label)
            transfer_flags(k, new_k)
            try:
                new_k.setValue(k.value())
            except TypeError:
                pass

            self.addKnob(new_k)

        self.addKnob(nuke.EndTabGroup_Knob(''))

        self._rename_knob = nuke.EvalString_Knob('', b'重命名')
        self.addKnob(self._rename_knob)
        self.addKnob(nuke.ColorChip_Knob('tile_color', b'节点颜色'))
        self.addKnob(nuke.ColorChip_Knob('gl_color', b'框线颜色'))
        k = nuke.PyScript_Knob('ok', 'OK')
        k.setFlag(nuke.STARTLINE)
        self.addKnob(k)
        self.addKnob(nuke.PyScript_Knob(
            'cancel', 'Cancel', 'nuke.tabClose()'))

    def knobChanged(self, knob):
        """Override. """
        if knob is self['ok']:
            try:
                self.execute()
                self.destroy()
            except CancelledError:
                pass
        else:
            self._values[knob.name()] = knob.value()

    @undoable_func('同时编辑多个节点')
    def execute(self):
        for n in progress(self.nodes, '设置节点'):
            set_knobs(n, **self._values)
            new_name = self._rename_knob.evaluate()
            if new_name:
                try:
                    n.setName(new_name)
                except ValueError:
                    nuke.message(b'非法名称, 已忽略')


def same_class_filter(nodes, node_class=None):
    """Filter nodes to one class."""

    classes = list(
        set([n.Class() for n in nodes if not node_class or n.Class() == node_class]))
    classes.sort()
    if len(classes) > 1:
        choice = nuke.choice(b'选择节点分类', b'节点分类', classes, default=0)
        if choice is not None:
            nodes = [n for n in nodes if n.Class()
                     == classes[choice]]
        else:
            nodes = [n for n in nodes if n.Class()
                     == nodes[0].Class()]
    return nodes
