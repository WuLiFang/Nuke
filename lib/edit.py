# -*- coding: UTF-8 -*-
"""Edit existed content in workfile."""

import os
import re
import colorsys
import random
import logging

import nuke

from wlf.notify import Progress

import callback

__version__ = '1.7.9'
LOGGER = logging.getLogger('com.wlf.edit')


def rename_all_nodes():
    """Rename all nodes by them belonged backdrop node ."""

    for i in nuke.allNodes('BackdropNode'):
        _nodes = i.getNodes()
        j = i['label'].value().split('\n')[0].split(' ')[0]
        for k in _nodes:
            if k.Class() == 'Group' and not '_' in k.name() and not (k['disable'].value()):
                name = k.name().rstrip('0123456789')
                k.setName(name + '_' + j + '_1', updateExpressions=True)
            elif not '_' in k.name() \
                    and (not nuke.exists(k.name() + '.disable') or not (k['disable'].value())):
                k.setName(k.Class() + '_' + j + '_1', updateExpressions=True)


def swap_knob_value(knob_a, knob_b):
    """Swap two same type knob value."""
    value_a, value_b = knob_a.value(), knob_b.value()
    knob_a.setValue(value_b)
    knob_b.setValue(value_a)


def update_toolsets(toolset_name, toolset_path):
    """Replace name matched node with given toolset."""

    for i in nuke.allNodes():
        if toolset_name in i.name() and 'python' not in i['label'].value():
            i.selectOnly()
            n = nuke.loadToolset(toolset_path)
            for k in i.allKnobs():
                knob_name = k.name()
                if knob_name in ['name', '', 'label']:
                    pass
                elif knob_name in n.knobs():
                    n[knob_name].setValue(i[knob_name].value())
            nuke.delete(i)


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
        """Record current active viewer status."""

        self.viewer = nuke.activeViewer()
        if self.viewer:
            self.node = self.viewer.node()
            self.inputs = self.node.input(0)
            for knob in self.node.allKnobs():
                self.knob_values[knob] = knob.value()

    def recover(self):
        """Recover viewer status to last record."""

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


def format_channel_name(text):
    """Return formatted text with nuke standard.  """

    ret = text
    ret = ret.replace(' ', '_')
    ret = '{0[0]}{0[1]}{1}'.format(
        ret.partition('.')[:-1], ret.partition('.')[-1].replace('.', '_'))
    return ret


def crate_copy_from_dict(dict_, input_node):
    """Create multiple Copy node from @dict_.  """

    def _rgba_order(channel):
        ret = channel
        repl = (('.red', '.0_'), ('.green', '.1_'),
                ('.blue', '.2_'), ('.alpha', '3_'))
        ret = reduce(lambda text, repl: text.replace(*repl), repl, ret)
        return ret

    count = 0
    n = input_node
    new_names_dict = {
        k:
        format_channel_name(v) if '.' in v else 'mask_extra.{}'.format(v)
        for k, v in dict_.items() if v}
    old_names = sorted(new_names_dict.keys(), key=_rgba_order)

    for old_name in old_names:
        new_name = new_names_dict[old_name]
        index = count % 4
        if not index:
            n = nuke.nodes.Copy(inputs=[n, n])
        n['from{}'.format(index)].setValue(old_name)
        add_channel(new_name)
        n['to{}'.format(index)].setValue(new_name)
        count += 1
    return n


def add_channel(name):
    """Add channel to nuke from a (Layer).(channel) string.  """

    layer = name.split('.')[0]
    nuke.Layer(layer, [name])


def add_layer(layername):
    """Add layer to nuke from @layername.  """

    if layername == 'depth':
        channels = ['depth.z']
    else:
        channels = list('{}.{}'.format(layername, channel)
                        for channel in ('red', 'green', 'blue', 'alpha'))
    nuke.Layer(layername, channels)


def replace_node(node, repl_node):
    """Replace all nodes except @repl_node input to @node with @repl_node."""

    for n in nuke.allNodes():
        if n is repl_node:
            continue
        for i in range(n.inputs()):
            if n.input(i) is node:
                n.setInput(i, repl_node)


def split_by_backdrop():
    """Split workfile to multiple file by backdrop."""

    text_saveto = '保存至:'
    text_ask_if_create_new_folder = '目标文件夹不存在, 是否创建?'

    # Panel
    panel = nuke.Panel('splitByBackdrop')
    panel.addFilenameSearch(text_saveto, os.getenv('TEMP'))
    panel.show()

    # Save splited .nk file
    save_path = panel.value(text_saveto).rstrip('\\/')
    noname_count = 0
    for i in nuke.allNodes('BackdropNode'):
        label = repr(i['label'].value()).strip(
            "'").replace('\\', '_').replace('/', '_')
        if not label:
            noname_count += 1
            label = 'noname_{0:03d}'.format(noname_count)
        if not os.path.exists(save_path):
            if not nuke.ask(text_ask_if_create_new_folder):
                return False
        dir_ = save_path + '/splitnk/'
        dir_ = os.path.normcase(dir_)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        filename = dir_ + label + '.nk'
        i.selectOnly()
        i.selectNodes()
        nuke.nodeCopy(filename)
    os.system('explorer "' + dir_ + '"')
    return True


def link_zdefocus():
    """Link all zdefocus node to '_ZDefocus' node."""

    n = nuke.toNode('_ZDefocus')
    if not n:
        return False
    for i in nuke.allNodes('ZDefocus2'):
        if i.name().startswith('_'):
            continue
        i['size'].setExpression('_ZDefocus.size')
        i['max_size'].setExpression('_ZDefocus.max_size')
        i['disable'].setExpression(
            '( [ exists _ZDefocus ] ) ? !_ZDefocus.disable : 0')
        i['center'].setExpression(
            '( [exists _ZDefocus] ) ? _ZDefocus.center : 0')
        i['dof'].setExpression(
            '( [exists _ZDefocus] ) ? _ZDefocus.dof : 0')
        i['label'].setValue('[\n'
                            'set trg parent._ZDefocus\n'
                            'if { [ exists $trg ] } {\n'
                            '    knob this.math [value $trg.math]\n'
                            '    knob this.z_channel [value $trg.z_channel]\n'
                            '}\n'
                            ']')
    return True


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
    """Set node glcolor a random hue color."""

    if 'gl_color' in n.knobs()\
            and not n['gl_color'].value()\
            and not n.name().startswith('_'):

        color = colorsys.hsv_to_rgb(random.random(), 0.8, 1)
        color = tuple(int(i * 255) for i in color)
        n['gl_color'].setValue(
            color[0] << 24 | color[1] << 16 | color[2] << 8)


def enable_rsmb(prefix='_'):
    """Enable all rsmb node with given prefix."""

    for i in nuke.allNodes('OFXcom.revisionfx.rsmb_v3'):
        if i.name().startswith(prefix):
            i['disable'].setValue(False)


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

    task = Progress('清除无用节点')
    if nodes is None:
        nodes = nuke.allNodes()
    count = 0
    while True:
        total = len(nodes)
        for index, n in enumerate(nodes):
            task.set(index * 100 / total, n.name())
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
            '<font size=5>删除了 {} 个未使用的节点。</font>\n'
            '<i>名称以"_"(下划线)开头的节点及其上游节点将不会被删除</i>'.format(count))


def replace_sequence():
    '''
    Replace all read node to specified frame range sequence.
    '''
    # Prepare Panel
    panel = nuke.Panel('单帧替换为序列')
    render_path_text = '限定只替换此文件夹中的读取节点'
    panel.addFilenameSearch(render_path_text, 'z:/SNJYW/Render/')
    first_text = '设置工程起始帧'
    panel.addExpressionInput(first_text, int(
        nuke.Root()['first_frame'].value()))
    last_text = '设置工程结束帧'
    panel.addExpressionInput(last_text, int(nuke.Root()['last_frame'].value()))

    confirm = panel.show()
    if confirm:
        render_path = os.path.normcase(panel.value(render_path_text))

        first = int(panel.value(first_text))
        last = int(panel.value(last_text))
        flag_frame = None

        nuke.Root()['proxy'].setValue(False)
        nuke.Root()['first_frame'].setValue(first)
        nuke.Root()['last_frame'].setValue(last)

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
                n['file'].setValue(file_path)
                n['format'].setValue('HD_1080')
                n['first'].setValue(first)
                n['origfirst'].setValue(first)
                n['last'].setValue(last)
                n['origlast'].setValue(last)

        n = nuke.toNode('_Write')
        if n:
            if flag_frame:
                flag_frame = int(flag_frame)
                n['custom_frame'].setValue(flag_frame)
                nuke.frame(flag_frame)
            n['use_custom_frame'].setValue(True)


def set_project_root_by_name(path='E:'):
    """Set project root by underscore splitted filename."""

    nuke.root()['project_directory'].setValue(os.path.dirname(
        path + '/' + os.path.basename(nuke.scriptName()).split('.')[0].replace('_', '/')))


def split_layers(node):
    """Create Shuffle node for all layers in node @n.  """

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
        n = nuke.nodes.Shuffle(
            inputs=[node], **kwargs)
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


def nodes_to_relpath(nodes):
    """Convert given nodes's file knob to relative path."""

    perfix = r'[value root.project_directory]'
    proj_dir = nuke.root().knob('project_directory').getValue()
    for read_node in nodes:
        if read_node.knob('file') is not None:
            old_path = read_node.knob('file').getValue()
            new_path = old_path.replace(proj_dir, perfix)
            read_node.knob('file').setValue(new_path)


def nodes_add_dots(nodes=None):
    """Add dots to orgnize node tree."""

    if not nodes:
        nodes = nuke.selectedNodes()

    def _add_dot(output_node, input_num):
        input_node = output_node.input(input_num)
        if not input_node\
                or input_node.Class() in ['Dot']\
                or abs(output_node.xpos() - input_node.xpos()) < output_node.screenWidth()\
                or abs(output_node.ypos() - input_node.ypos()) <= output_node.screenHeight():
            return None
        if output_node.Class() in ['Viewer'] or output_node['hide_input'].value():
            return None

        _dot = nuke.nodes.Dot(inputs=[input_node])
        output_node.setInput(input_num, _dot)
        _dot.setXYpos(
            input_node.xpos() + input_node.screenWidth() / 2 - _dot.screenWidth() / 2,
            output_node.ypos() + output_node.screenHeight() / 2 - _dot.screenHeight() /
            2 - (_dot.screenHeight() + 5) * input_num
        )

    def _all_input_add_dot(node):
        for input_num in range(node.inputs()):
            _add_dot(node, input_num)

    for n in nodes:
        if n.Class() in ['Dot']:
            continue
        _all_input_add_dot(n)


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

    callback.clean()

    return _group


def all_gizmo_to_group():
    """Convert all gizmo node to group node."""

    for n in nuke.allNodes():
        # Avoid scripted gizmo.
        if nuke.knobChangeds.get(n.Class()):
            continue

        gizmo_to_group(n)


def mark_enable(nodes):
    """Mark selected node enable on script save.  """
    if isinstance(nodes, nuke.Node):
        nodes = (nodes)
    for n in nodes:
        old_name = n.name()
        if not old_name.startswith('_enable_'):
            n.setName('_enable_{}'.format(old_name))
        try:
            n['disable'].setValue(True)
        except AttributeError:
            pass


def disable_nodes(prefix):
    """Disable multiple nodes.  """

    for n in nuke.allNodes():
        if n.name().startswith(prefix):
            try:
                n['disable'].setValue(True)
            except AttributeError:
                pass


def autoplace_all():
    """Place all nodes position so them won't overlap."""

    for n in nuke.allNodes():
        nuke.autoplace(n)


def insert_node(node, input_node):
    """Insert @node after @input_node."""

    for n in nuke.allNodes():
        for i in range(n.inputs()):
            if n.input(i) == input_node:
                n.setInput(i, node)

    node.setInput(0, input_node)


def get_max(node, channel='rgb'):
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
    """Copy @input1 / (@layer or rgba) to @input0 / @layer.  """

    output = output or layer
    input1 = input1 or input0
    if input0 is input1 and layer == output and layer in nuke.layers(input0):
        return input0

    def _input1_layer(layer):
        if layer in nuke.layers(input1):
            return layer

    add_layer(output)
    input_channel = _input1_layer(layer) or _input1_layer(output) or 'rgba'
    if input0 is input1:
        _d = {"in": input_channel}
        ret = nuke.nodes.Shuffle(inputs=[input1], out=output, **_d)
    else:
        ret = nuke.nodes.Merge2(
            tile_color=0x9e3c63ff,
            inputs=[input0, input1], operation='copy',
            Achannels=_input1_layer(layer) or _input1_layer(output) or 'rgba',
            Bchannels='none', output=output, label=layer)
    return ret


def set_knobs(node, values):
    """Set @node knobs from @values.  """
    value_dict = dict()
    value_dict.update(values)
    for knob_name, value in value_dict.items():
        try:
            node[knob_name].setValue(value)
        except (AttributeError, NameError, TypeError):
            LOGGER.debug('Can not set knob: %s.%s to %s',
                         node.name(), knob_name, value)


def same_class_filter(nodes, node_class=None):
    """Filter nodes to one class."""
    classes = list(
        set([n.Class() for n in nodes if not node_class or n.Class() == node_class]))
    classes.sort()
    if len(classes) > 1:
        choice = nuke.choice('选择节点分类', '节点分类', classes, default=0)
        if choice is not None:
            nodes = [n for n in nodes if n.Class()
                     == classes[choice]]
        else:
            nodes = [n for n in nodes if n.Class()
                     == nodes[0].Class()]
    return nodes


def transfer_flags(src, dst):
    """Transfer @src knob flags to @dst.  """
    for flag in [pow(2, n) for n in range(31)]:
        if src.getFlag(flag):
            dst.setFlag(flag)
        else:
            dst.clearFlag(flag)


def _print_flags():
    import math
    for attr in sorted(dir(nuke), key=lambda x: getattr(nuke, x)):
        value = getattr(nuke, attr)
        if isinstance(value, int) and value > 0:
            _log = math.log(value, 2)
            if int(_log) == _log:
                print(attr, value)
