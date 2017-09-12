# -*- coding: UTF-8 -*-
"""UI for edit operation."""

import nuke
import nukescripts
from edit import crate_copy_from_dict, replace_node, CurrentViewer

__version__ = '0.1.1'


class ChannelsRenamePanel(nukescripts.PythonPanel):
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
        nuke.Undo.disable()
        nukescripts.PythonPanel.__init__(
            self, '重命名通道', 'com.wlf.channels_rename')

        viewer = CurrentViewer()
        self._viewer = viewer

        self._node = node or nuke.selectedNode()
        n = self._node
        self._channels = sorted((channel for channel in n.channels()
                                 if channel.startswith(prefix)), key=_pannel_order)

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
        k = nuke.PyScript_Knob('ok', 'OK', 'nuke.tabClose()')
        k.setFlag(nuke.STARTLINE)
        self.addKnob(k)
        self.addKnob(nuke.PyScript_Knob(
            'cancel', 'Cancel', 'nuke.tabClose()'))
        self._knobs = self.knobs()

        nuke.Undo.enable()

    def knobChanged(self, knob):
        """Override. """
        if knob in (self._knobs['ok'], self._knobs['cancel']):
            nuke.Undo.disable()
            try:
                nuke.delete(self._layercontactsheet)
            except ValueError:
                pass
            self._viewer.recover()
            nuke.Undo.enable()
            if knob is self._knobs['ok']:
                nuke.Undo.begin()
                nuke.Undo.name('重命名通道')
                n = crate_copy_from_dict(self.rename_dict, self._node)
                replace_node(self._node, n)
                nuke.Undo.end()

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
            super(ChannelsRenamePanel, self).show()
