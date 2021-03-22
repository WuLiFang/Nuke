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
import six
import cast_unknown as cast

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Tuple, Iterable, Any, Dict, List


class ChannelsRename(PythonPanel):
    """Dialog UI of channel_rename."""

    widget_id = 'com.wlf.channels_rename'

    def __init__(
        self,
        prefix=('PuzzleMatte', 'ID'),  # type: Tuple[Text, ...]
        node=None,  # type: nuke.Node
    ):
        def _pannel_order(
            name,  # type: Text
        ):
            return (
                name.endswith('.alpha'),
                name.startswith(prefix),
                name.split('.')[0],
                name.endswith('.blue'),
                name.endswith('.green'),
                name.endswith('.red'),
            )

        def _stylize(text):
            # type: (Text) -> Text
            ret = text
            repl = {'.red': '.<span style=\"color:#FF4444\">red</span>',
                    '.green':  '.<span style=\"color:#44FF44\">green</span>',
                    '.blue': '.<span style=\"color:#4444FF\">blue</span>'}
            for k, v in six.iteritems(repl):
                ret = ret.replace(k, v)
            return ret

        super(ChannelsRename, self).__init__(
            cast.binary('重命名通道'), cast.binary(self.widget_id))

        viewer = CurrentViewer()
        n = node or nuke.selectedNode()
        self._channels = sorted((cast.text(channel) for channel in n.channels()
                                 if cast.text(channel).startswith(prefix)),
                                key=_pannel_order) + ['rgba.alpha']
        self._node = n
        self._viewer = viewer

        nuke.Undo.disable()

        n = nuke.nodes.LayerContactSheet(inputs=[n], showLayerNames=1)
        self._layercontactsheet = n

        viewer.link(n)
        if viewer.node:
            _ = cast.not_none(viewer.node[b'channels']).setValue('rgba')

        for channel in self._channels:
            self.addKnob(nuke.String_Knob(
                cast.binary(channel), cast.binary(_stylize(channel)), b''))
            if channel.endswith('.blue'):
                self.addKnob(nuke.Text_Knob(b''))
        self.addKnob(nuke.Text_Knob(b''))
        k = nuke.Script_Knob(b'ok', b'OK')
        k.setFlag(nuke.STARTLINE)
        self.addKnob(k)
        k = nuke.Script_Knob(b'cancel', b'Cancel')
        self.addKnob(k)

        nuke.Undo.enable()

        self.add_callbacks()

    def add_callbacks(self):
        """Add nuke callbacks.  """

        nuke.removeOnDestroy(ChannelsRename.hide, args=(self,))
        nuke.addOnUserCreate(ChannelsRename.hide, args=(self,))

    def remove_callbacks(self):
        """Remove nuke callbacks.  """

        nuke.removeOnDestroy(ChannelsRename.hide, args=(self,))
        nuke.removeOnUserCreate(ChannelsRename.hide, args=(self,))

    def destroy(self):
        """Destroy the panel.  """

        if not is_node_deleted(self._layercontactsheet):
            nuke.Undo.disable()
            self._layercontactsheet[b'label'].setValue('[delete this]')
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

    def __init__(
        self,
        nodes=None,  # type: Iterable[nuke.Node]
    ):
        super(MultiEdit, self).__init__(
            cast.binary('多节点编辑'), cast.binary(self.widget_id))

        nodes = cast.list_(nodes or nuke.selectedNodes(), nuke.Node)
        assert nodes, 'Nodes not given. '
        nodes = same_class_filter(nodes)
        self.nodes = nodes
        self._values = {}  # type: Dict[Text, Any]

        knobs = nodes[0].allKnobs()

        self.addKnob(nuke.Text_Knob(b'', cast.binary(
            '以 {} 为模版'.format(nodes[0].name()))))
        self.addKnob(nuke.Tab_Knob(b'', nodes[0].Class()))

        def _tab_knob():
            if label is None:
                new_k = nuke.Tab_Knob(name, label, nuke.TABENDGROUP)
            elif label.startswith(b'@b;'):
                new_k = nuke.Tab_Knob(name, label, nuke.TABBEGINGROUP)
            else:
                new_k = knob_class(name, label)
            return new_k

        for k in knobs:
            name = k.name()
            label = k.label() or None

            knob_class = getattr(nuke, type(k).__name__)

            if isinstance(k, (nuke.Script_Knob, nuke.Obsolete_Knob)) \
                    or knob_class is nuke.Knob:
                continue
            elif isinstance(k, nuke.Channel_Knob):
                new_k = nuke.Channel_Knob(name, label, k.depth())
            elif isinstance(k, nuke.Enumeration_Knob):
                enums = [k.enumName(i) for i in range(k.numValues())]
                new_k = knob_class(name, label, enums)
            elif isinstance(k, nuke.Tab_Knob):
                new_k = _tab_knob()
            elif isinstance(k, nuke.Array_Knob):
                new_k = knob_class(name, label)
                new_k.setRange(k.min(), k.max())
            else:
                # print(knob_class, name, label)
                new_k = knob_class(name, label)
            transfer_flags(k, new_k)
            try:
                _ = new_k.setValue(k.value())
            except TypeError:
                pass

            self.addKnob(new_k)

        self.addKnob(nuke.EndTabGroup_Knob(b''))

        self._rename_knob = nuke.EvalString_Knob(b'', cast.binary('重命名'))
        self.addKnob(self._rename_knob)
        self.addKnob(nuke.ColorChip_Knob(b'tile_color', cast.binary('节点颜色')))
        self.addKnob(nuke.ColorChip_Knob(b'gl_color', cast.binary('框线颜色')))
        k = nuke.PyScript_Knob(b'ok', b'OK')
        k.setFlag(nuke.STARTLINE)
        self.addKnob(k)
        self.addKnob(nuke.PyScript_Knob(
            b'cancel', b'Cancel', b'nuke.tabClose()'))

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
                    nuke.message(cast.binary('非法名称, 已忽略'))


def same_class_filter(
    nodes,  # type: Iterable[nuke.Node]
    node_class=None,  # type: Text
):  # type: (...) -> List[nuke.Node]
    """Filter nodes to one class."""

    nodes = cast.list_(nodes, nuke.Node)
    classes = list(
        set([n.Class() for n in nodes if not node_class or n.Class() == cast.binary(node_class)]))
    classes.sort()
    if len(classes) > 1:
        choice = nuke.choice(cast.binary('选择节点分类'),
                             cast.binary('节点分类'), classes, default=0)
        if choice is not None:
            nodes = [n for n in nodes if n.Class()
                     == classes[choice]]
        else:
            nodes = [n for n in nodes if n.Class()
                     == nodes[0].Class()]
    return nodes
