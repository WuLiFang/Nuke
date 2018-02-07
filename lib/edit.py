# -*- coding: UTF-8 -*-
"""Edit existed content in workfile."""
from __future__ import absolute_import, print_function, unicode_literals

import colorsys
import logging
import math
import os
import random
import re
import threading
from functools import wraps

import nuke

from node import wlf_write_node
from nuketools import Nodes, undoable_func, utf8
from wlf.notify import get_default_progress_handler, progress
from wlf.path import get_unicode as u
from wlf.path import PurePath

LOGGER = logging.getLogger('com.wlf.edit')
ENABLE_MARK = '_enable_'


def add_channel(name):
    """Add a channel from `{layer}.{channel}` format string.

    Args:
        name (str): Channel name.
    """

    try:
        name = str(name).encode('ascii')
    except (UnicodeDecodeError, UnicodeEncodeError):
        raise ValueError('Non-ascii character not acceptable.')

    try:
        layer, channel = name.split('.', 1)
    except ValueError:
        layer, channel = 'other', name
    if '.' in channel:
        raise ValueError('Wrong channel format.', name)
    nuke.Layer(layer, [name])


def add_layer(layername):
    """Add layer to nuke from @layername.  

    Returns:
        nuke.Layer or None: Added layer.
    """

    if layername in nuke.layers():
        return

    channels = ['{}.{}'.format(layername, channel)
                for channel in ('red', 'green', 'blue', 'alpha')]
    return nuke.Layer(layername, channels)


class CurrentViewer(object):
    """Manipulate currunt viewer."""

    viewer = None
    node = None
    inputs = None
    knob_values = None

    def __init__(self):
        self.knob_values = {}
        self.record()

    def link(self, input_node, input_num=0, replace=True):
        """Connet input_node to viewer.input0 the activate it, create viewer if needed."""

        if self.viewer:
            n = self.node
        else:
            viewers = nuke.allNodes('Viewer')
            if viewers:
                n = viewers[0]
            else:
                n = nuke.nodes.Viewer()
        self.node = n

        if replace or not n.input(input_num):
            n.setInput(input_num, input_node)
            try:
                nuke.activeViewer().activateInput(input_num)
            except AttributeError:
                pass

    def record(self):
        """Record current active viewer state."""

        self.viewer = nuke.activeViewer()
        if self.viewer:
            self.node = self.viewer.node()
            self.inputs = self.node.input(0)
            for knob in self.node.allKnobs():
                self.knob_values[knob] = knob.value()

    def recover(self):
        """Recover viewer state to last record."""

        if self.viewer:
            self.node.setInput(
                0, self.inputs)
            for knob, value in self.knob_values.items():
                try:
                    knob.setValue(value)
                except TypeError:
                    pass
        else:
            nuke.delete(self.node)


def escape_for_channel(text):
    """Escape text for channel name.

    Args:
        text (str): Text for escaped

    Returns:
        str: Esacped text.

    Example:
        >>> escape_for_channel('apple')
        'mask_extra.apple'
        >>> escape_for_channel('tree.apple')
        'tree.apple'
        >>> escape_for_channel('tree.apple.leaf')
        'tree.apple_leaf'
        >>> escape_for_channel('tree.apple.leaf.根')
        'tree.apple_leaf_?'
        >>> escape_for_channel(None)
        'mask_extra.None'

    """

    ret = u(text)
    if '.' not in ret:
        ret = 'mask_extra.{}'.format(ret)
    ret = ret.replace(' ', '_')
    ret = '{0[0]}{0[1]}{1}'.format(
        ret.partition('.')[:-1], ret.partition('.')[-1].replace('.', '_'))
    ret = ret.encode('ascii', 'replace')
    return ret


def named_copy(n, names_dict):
    """Create multiple Copy node on demand.

    Args:
        n (nuke.Node): Node as input.
        names_dict (dict[str:str]): A dict with source channel name as key,
            target channel name as value.

    Returns:
        nuke.Node: Output node.
    """

    def _rgba_order(channel):
        ret = channel
        repl = (('.red', '.0_'), ('.green', '.1_'),
                ('.blue', '.2_'), ('.alpha', '3_'))
        ret = reduce(lambda text, repl: text.replace(*repl), repl, ret)
        return ret

    # For short version channel name.
    convert_dict = {
        'r': 'rgba.red',
        'g': 'rgba.green',
        'b': 'rgba.blue',
        'a': 'rgba.alpha',
        'red': 'rgba.red',
        'green': 'rgba.green',
        'blue': 'rgba.blue',
        'alpha': 'rgba.alpha',
    }

    # Escape input
    names_dict = {
        convert_dict.get(k, k): escape_for_channel(v)
        for k, v in names_dict.items() if v}

    for i, k in enumerate(sorted(names_dict, key=_rgba_order)):
        v = names_dict[k]

        index = i % 4
        if not index:
            n = nuke.nodes.Copy(inputs=[n, n])
        n['from{}'.format(index)].setValue(k)
        add_channel(v)
        n['to{}'.format(index)].setValue(v)
    return n


def replace_node(node, repl_node):
    """Replace a node with another in node graph.

    Args:
        node (nuke.Node): Node to be replaced.
        repl_node (nuke.Node): Node to replace.
    """

    if not (isinstance(node, nuke.Node)
            and isinstance(repl_node, nuke.Node)):
        raise TypeError('Expect two nuke.Node, got: {} and {}'.format(
            type(node), type(repl_node)))

    nodes = node.dependent(nuke.INPUTS | nuke.HIDDEN_INPUTS, False)
    for n in nodes:
        for i in range(n.inputs()):
            if n.input(i) is node:
                n.setInput(i, repl_node)


def get_min_max(src_node, channel='depth.Z'):
    '''
    Return the min and max values of a given node's image as a tuple

    args:
       src_node  - node to analyse
       channels  - channels to analyse. This can either be a channel or layer name
    '''
    min_color = nuke.nodes.MinColor(
        channels=channel, target=0, inputs=[src_node])
    inv = nuke.nodes.Invert(channels=channel, inputs=[src_node])
    max_color = nuke.nodes.MinColor(channels=channel, target=0, inputs=[inv])

    cur_frame = nuke.frame()
    nuke.execute(min_color, cur_frame, cur_frame)
    min_v = -min_color['pixeldelta'].value()

    nuke.execute(max_color, cur_frame, cur_frame)
    max_v = max_color['pixeldelta'].value() + 1

    for n in (min_color, max_color, inv):
        nuke.delete(n)
    return min_v, max_v


def set_random_glcolor(n):
    """Set glcolor of node to a hue random color. 

    Args:
        n (nuke.Node): Node to manipulate.
    """

    if ('gl_color' in n.knobs()
            and not n['gl_color'].value()
            and not n.name().startswith('_')):

        color = colorsys.hsv_to_rgb(random.random(), 0.8, 1)
        color = tuple(int(i * 255) for i in color)
        n['gl_color'].setValue(
            color[0] << 24 | color[1] << 16 | color[2] << 8)


def clear_selection():
    """Clear node selection.  """

    for n in nuke.allNodes():
        try:
            selected = n['selected'].value()
        except NameError:
            continue
        if selected:
            n['selected'].setValue(False)


def delete_unused_nodes(nodes=None, message=False):
    # TODO: Need refactor and test.
    """Delete all unused nodes."""

    def _is_used(n):
        if n.name().startswith('_')\
                or n.Class() in \
                ['BackdropNode', 'Read', 'Write', 'Viewer', 'GenerateLUT', 'wlf_Write']\
                or n.name() == 'VIEWER_INPUT':
            return True
        nodes_dependent_this = (n for n in n.dependent()
                                if n.Class() not in [''] or n.name().startswith('_'))
        return any(nodes_dependent_this)

    if nodes is None:
        nodes = nuke.allNodes()
    count = 0
    handler = get_default_progress_handler()
    handler.message_factory = lambda n: n.name()
    while True:
        for n in progress(nodes, '清除无用节点', handler):
            if not _is_used(n):
                nuke.delete(n)
                nodes.remove(n)
                count += 1
                break
        else:
            break

    print('Deleted {} unused nodes.'.format(count))
    if message:
        nuke.message(
            b'<font size=5>删除了 {} 个未使用的节点。</font>\n'
            b'<i>名称以"_"(下划线)开头的节点及其上游节点将不会被删除</i>'.format(count))


def replace_sequence():
    # TODO: Need refactor and test.
    '''Replace all read node to specified frame range sequence.  '''

    # Prepare Panel
    panel = nuke.Panel(b'单帧替换为序列')
    render_path_text = '限定只替换此文件夹中的读取节点'
    panel.addFilenameSearch(utf8(render_path_text), 'z:/SNJYW/Render/')
    first_text = '设置工程起始帧'
    panel.addExpressionInput(utf8(first_text), int(
        nuke.Root()['first_frame'].value()))
    last_text = '设置工程结束帧'
    panel.addExpressionInput(utf8(last_text), int(
        nuke.Root()['last_frame'].value()))

    confirm = panel.show()
    if confirm:
        render_path = os.path.normcase(panel.value(render_path_text))

        first = int(panel.value(first_text))
        last = int(panel.value(last_text))
        flag_frame = None

        nuke.Root()[b'proxy'].setValue(False)
        nuke.Root()[b'first_frame'].setValue(first)
        nuke.Root()[b'last_frame'].setValue(last)

        for n in nuke.allNodes('Read'):
            file_path = nuke.filename(n)
            if os.path.normcase(file_path).startswith(render_path):
                search_result = re.search(r'\.([\d]+)\.', file_path)
                if search_result:
                    flag_frame = search_result.group(1)
                file_path = re.sub(
                    r'\.([\d#]+)\.',
                    lambda matchobj: r'.%0{}d.'.format(len(matchobj.group(1))),
                    file_path)
                n[b'file'].setValue(file_path)
                n[b'format'].setValue(b'HD_1080')
                n[b'first'].setValue(first)
                n[b'origfirst'].setValue(first)
                n[b'last'].setValue(last)
                n[b'origlast'].setValue(last)

        n = wlf_write_node()
        if n:
            if flag_frame:
                flag_frame = int(flag_frame)
                n[b'custom_frame'].setValue(flag_frame)
                nuke.frame(flag_frame)
            n[b'use_custom_frame'].setValue(True)


def split_layers(node):
    """Create Shuffle node for each layers in node @n.  """

    ret = []

    for layer in nuke.layers(node):
        if layer in ['rgb', 'rgba', 'alpha']:
            continue
        kwargs = {'in': layer,
                  'label': layer}
        try:
            kwargs['postage_stamp'] = node['postage_stamp'].value()
        except NameError:
            pass
        n = nuke.nodes.Shuffle(inputs=[node], **kwargs)
        ret.append(n)
    return ret


def shuffle_rgba(node):
    """Create rgba shuffle."""

    channels = ('red', 'green', 'blue', 'alpha')
    ret = []

    for channel in channels:
        kwargs = {'label': channel}
        for i in channels:
            kwargs[i] = channel
        try:
            kwargs['postage_stamp'] = node['postage_stamp'].value()
        except NameError:
            pass
        n = nuke.nodes.Shuffle(inputs=[node], **kwargs)
        ret.append(n)

    return ret


def use_relative_path(nodes):
    """Convert given nodes's file knob to relative path."""

    if isinstance(nodes, nuke.Node):
        nodes = [nodes]

    proj_dir = PurePath(nuke.value('root.project_directory'))
    for n in nodes:
        try:
            path = PurePath(n['file'].value())
            n['file'].setValue(utf8(path.relative_to(proj_dir).as_posix()))
        except NameError:
            continue


def gizmo_to_group(gizmo):
    """Convert given gizmo node to gruop node."""

    if not isinstance(gizmo, nuke.Gizmo):
        return gizmo

    _selected = gizmo['selected'].value()
    _group = gizmo.makeGroup()

    # Set Input.
    for i in range(gizmo.inputs()):
        _group.setInput(i, gizmo.input(i))
    # Set Output.
    for n in nuke.allNodes():
        for i in range(n.inputs()):
            if n.input(i) is gizmo:
                n.setInput(i, _group)

    # Set position and name.
    if gizmo.shown():
        _group.showControlPanel()
    _group.setXYpos(gizmo.xpos(), gizmo.ypos())
    _name = gizmo['name'].value()
    nuke.delete(gizmo)
    _group.setName(_name)
    _group['selected'].setValue(_selected)

    return _group


def all_gizmo_to_group():
    """Convert all gizmo node to group node."""

    for n in nuke.allNodes():
        # Avoid scripted gizmo.
        if nuke.knobChangeds.get(n.Class()):
            continue

        gizmo_to_group(n)


def mark_enable(nodes):
    """Mark nodes enable later then disabled them.  """

    if isinstance(nodes, nuke.Node):
        nodes = (nodes)
    for n in nodes:
        try:
            label_knob = n['label']
            label = label_knob.value()
            if ENABLE_MARK not in label:
                label_knob.setValue('{}\n{}'.format(label, ENABLE_MARK))
            n['disable'].setValue(True)
        except NameError:
            continue


def marked_nodes():
    """ Get marked nodes.

    Returns:
        Nodes: maked nodes.
    """

    ret = set()
    for n in nuke.allNodes():
        try:
            label = n['label'].value()
            name = n.name()
            _ = [ret.add(n) for i in (label, name) if ENABLE_MARK in i]
        except NameError:
            continue
    return Nodes(ret)


def insert_node(node, input_node):
    """Insert @node after @input_node in node graph

    Args:
        node (nuke.Node): Node to insert.
        input_node (nuke.Node): Node as input.
    """

    for n in nuke.allNodes():
        for i in xrange(n.inputs()):
            if n.input(i) is input_node:
                n.setInput(i, node)

    node.setInput(0, input_node)


def get_max(node, channel='rgb'):
    # TODO: Need test.
    '''
    Return themax values of a given node's image at middle frame

    @parm n: node
    @parm channel: channel for sample
    '''
    first = node.firstFrame()
    last = node.lastFrame()
    middle = (first + last) // 2
    ret = 0

    n = nuke.nodes.Invert(channels=channel, inputs=[node])
    n = nuke.nodes.MinColor(
        channels=channel, target=0, inputs=[n])

    for frame in (middle, first, last):
        try:
            nuke.execute(n, frame, frame)
        except RuntimeError:
            continue
        ret = max(ret, n['pixeldelta'].value() + 1)
        if ret > 0.7:
            break

    print(u'getMax({1}, {0}) -> {2}'.format(channel, node.name(), ret))

    nuke.delete(n.input(0))
    nuke.delete(n)

    return ret


def reload_all_read_node():
    """Reload all read node by reload button.  """

    for n in nuke.allNodes('Read'):
        n['reload'].execute()


def set_framerange(first, last, nodes=None):
    """Set read nodes framerange.  """

    if nodes is None:
        nodes = nuke.selectedNodes()
    first, last = int(first), int(last)
    for n in nodes:
        if n.Class() == 'Read':
            n['first'].setValue(first)
            n['origfirst'].setValue(first)
            n['last'].setValue(last)
            n['origlast'].setValue(last)


def dialog_set_framerange():
    """Dialog for set_framerange.  """

    panel = nuke.Panel('设置帧范围')
    panel.addExpressionInput('first', nuke.numvalue('root.first_frame'))
    panel.addExpressionInput('last', nuke.numvalue('root.last_frame'))
    confirm = panel.show()

    if confirm:
        set_framerange(panel.value('first'), panel.value('last'))


def copy_layer(input0, input1=None, layer='rgba', output=None):
    """Copy whole layer from a node to another.

    Args:
        input0 (nuke.Node): Source node
        input1 (nuke.Node, optional): Defaults to None. 
            If given, use source layer from this node.
        layer (str, optional): Defaults to 'rgba'. 
            Source layer name.
        output (str, optional): Defaults to None. 
            Output layer name. If not given, use same with source layer.

    Returns:
        nuke.Node: Final output node.
    """

    output = output or layer
    input1 = input1 or input0

    # Skip case that has no effect.
    if (input0 is input1
        and layer == output
            and layer in nuke.layers(input0)):
        return input0

    # Choice input channel name.
    try:
        input1_layers = nuke.layers(input1)
        input_channel = [i for i in (layer, output, 'rgba')
                         if i in input1_layers][0]
    except IndexError:
        raise ValueError('Can not find avaliable layer in input1',
                         input1_layers)

    add_layer(output)
    # Use shuffle if input0 is input1 else use merge.
    if input0 is input1:
        _d = {"in": input_channel}
        ret = nuke.nodes.Shuffle(inputs=[input1], out=output, **_d)
    else:
        ret = nuke.nodes.Merge2(
            tile_color=0x9e3c63ff,
            inputs=[input0, input1], operation='copy',
            Achannels=input_channel,
            Bchannels='none', output=output, label=layer)
    return ret


def set_knobs(node, **knob_values):
    """Set multiple knobs at once.

    Args:
        node (nuke.Node): Node to set knobs.
        **knob_values (any): Use pair of (knob name, value).
    """

    for knob_name, value in knob_values.items():
        try:
            node[knob_name].setValue(value)
        except (AttributeError, NameError, TypeError):
            LOGGER.debug('Can not set knob: %s.%s to %s',
                         node.name(), knob_name, value)


def transfer_flags(src, dst):
    """Transfer flag from knob to another.

    Args:
        src (nuke.Knob): Get flags from this knob.
        dst (nuke.Knob): Set flags to this knob.
    """

    assert isinstance(src, nuke.Knob)
    assert isinstance(dst, nuke.Knob)

    # Set all possible flag.
    for flag in [pow(2, n) for n in range(31)]:
        if src.getFlag(flag):
            dst.setFlag(flag)
        else:
            dst.clearFlag(flag)


def all_flags():
    """Get all flags in nuke.

    Returns:
        dict: Flag name as key, flag value as value.
    """

    ret = dict()

    for attr in sorted(dir(nuke), key=lambda x: getattr(nuke, x)):
        value = getattr(nuke, attr)
        if isinstance(value, int) and value > 0:
            _log = math.log(value, 2)
            if int(_log) == _log:
                ret[attr] = value

    return ret
