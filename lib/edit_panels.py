# -*- coding: UTF-8 -*-
"""UI for edit operation."""

import nuke
import nukescripts
from edit import crate_copy_from_dict, replace_node, CurrentViewer,\
    set_knobs, same_class_filter, transfer_flags
from wlf.notify import Progress, CancelledError

__version__ = '0.2.6'

if not nuke.GUI:
    nukescripts.PythonPanel = object


class ChannelsRename(nukescripts.PythonPanel):
    """Dialog UI of channel_rename."""

    def __init__(self, prefix='PuzzleMatte', node=None):
        def _pannel_order(name):
            ret = name.replace(prefix + '.', '!.')

            repl = ('.red', '.0_'), ('.green', '.1_'), ('.blue', '.2_')
            ret = reduce(lambda text, repl: text.replace(*repl), repl, ret)

            if ret.endswith('.alpha'):
                ret = '~{}'.format(ret)
            return ret

        def _stylize(text):
            ret = text
            repl = {'.red': '.<span style=\"color:#FF4444\">red</span>',
                    '.green':  '.<span style=\"color:#44FF44\">green</span>',
                    '.blue': '.<span style=\"color:#4444FF\">blue</span>'}
            for k, v in repl.iteritems():
                ret = ret.replace(k, v)
            return ret

        viewer = CurrentViewer()
        n = node or nuke.selectedNode()
        self._channels = sorted((channel for channel in n.channels()
                                 if channel.startswith(prefix)), key=_pannel_order) + ['rgba.alpha']
        self._node = n
        self._viewer = viewer

        nuke.Undo.disable()
        nukescripts.PythonPanel.__init__(
            self, '重命名通道', 'com.wlf.channels_rename')

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
        self.addKnob(nuke.Script_Knob('cancel', 'Cancel'))
        self._knobs = self.knobs()

        nuke.Undo.enable()

        nuke.addOnDestroy(ChannelsRename.destroy, args=(self))
        nuke.addOnUserCreate(ChannelsRename.destroy, args=(self))

    def __del__(self):
        nuke.removeOnDestroy(ChannelsRename.destroy, args=(self))
        nuke.removeOnUserCreate(ChannelsRename.destroy, args=(self))

    def destroy(self):
        """Destroy the panel.  """
        super(ChannelsRename, self).destroy()
        nuke.Undo.disable()
        self._layercontactsheet['label'].setValue('[delete this]')
        nuke.Undo.enable()
        self.__del__()

    def knobChanged(self, knob):
        """Override. """
        if knob in (self._knobs['ok'], self._knobs['cancel']):
            self._viewer.recover()
            if knob is self._knobs['ok']:
                nuke.Undo.begin()
                nuke.Undo.name('重命名通道')
                n = crate_copy_from_dict(self.rename_dict, self._node)
                replace_node(self._node, n)
                nuke.Undo.end()
            self.destroy()

    @property
    def rename_dict(self):
        """Dictionary for channels_rename().  """
        return {channel: self._knobs[channel].value() for channel in self._channels}

    def show(self):
        """Show self to user.  """
        pane = nuke.getPaneFor('Properties.1')
        if pane:
            self.addToPane(pane)
        else:
            self.addToPane(nuke.getPaneFor('Viewer.1'))


class MultiEdit(nukescripts.PythonPanel):
    """Edit multiple same class node at once.  """
    nodes = None

    def __init__(self, nodes=None):
        nukescripts.PythonPanel.__init__(
            self, '多节点编辑', 'com.wlf.multiedit')

        nodes = nodes or nuke.selectedNodes()
        assert nodes, 'Nodes not given. '
        nodes = same_class_filter(nodes)
        self.nodes = nodes
        self._values = {}

        knobs = nodes[0].allKnobs()

        self.addKnob(nuke.Text_Knob('', '以 {} 为模版'.format(nodes[0].name())))
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

        self._rename_knob = nuke.EvalString_Knob('', '重命名')
        self.addKnob(self._rename_knob)
        self.addKnob(nuke.ColorChip_Knob('tile_color', '节点颜色'))
        self.addKnob(nuke.ColorChip_Knob('gl_color', '框线颜色'))
        k = nuke.PyScript_Knob('ok', 'OK')
        k.setFlag(nuke.STARTLINE)
        self.addKnob(k)
        self.addKnob(nuke.PyScript_Knob(
            'cancel', 'Cancel', 'nuke.tabClose()'))

        self._knobs = self.knobs()

        nuke.addOnDestroy(MultiEdit.destroy, args=(self))

    def __del__(self):
        nuke.removeOnDestroy(MultiEdit.destroy, args=(self))

    def __getitem__(self, name):
        return self._knobs[name]

    def destroy(self):
        """Destroy the panel.  """
        super(MultiEdit, self).destroy()
        self.__del__()

    def knobChanged(self, knob):
        """Override. """
        if knob is self['ok']:
            nuke.Undo.begin()
            nuke.Undo.name('同时编辑多个节点')
            task = Progress('设置节点', total=len(self.nodes))
            for n in self.nodes:
                try:
                    task.step(n.name())
                except CancelledError:
                    nuke.Undo.cancel()
                    return
                set_knobs(n, self._values)
                new_name = self._rename_knob.evaluate()
                if new_name:
                    n.setName(new_name)
            nuke.Undo.end()
            self.destroy()
        else:
            self._values[knob.name()] = knob.value()

    def show(self):
        """Show self to user.  """
        pane = nuke.getPaneFor('Properties.1')
        if pane:
            self.addToPane(pane)
        else:
            self.addToPane(nuke.getPaneFor('Viewer.1'))
