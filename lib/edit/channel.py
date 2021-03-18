# -*- coding=UTF-8 -*-
"""Handle image channels.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

import cast_unknown as cast

import six

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import (Dict, Text, List)


def add_channel(
    name,  # type: six.text_type
):  # type: (...) -> None
    """Add a channel from `{layer}.{channel}` format string.

    Args:
        name (str): Channel name.
    """

    try:
        _ = six.text_type(name).encode('ascii')
    except (UnicodeDecodeError, UnicodeEncodeError):
        raise ValueError('Non-ascii character not acceptable.')

    try:
        layer, channel = name.split('.', 1)
    except ValueError:
        layer, channel = 'other', name
    if '.' in channel:
        raise ValueError('Wrong channel format.', name)
    _ = nuke.Layer(cast.binary(layer), [cast.binary(name)])


def add_layer(layername):
    """Add layer to nuke from @layername.

    Returns:
        nuke.Layer or None: Added layer.
    """

    if layername in nuke.layers():
        return

    channels = [cast.binary('{}.{}'.format(layername, channel))
                for channel in ('red', 'green', 'blue', 'alpha')]
    return nuke.Layer(layername, channels)


def escape_for_channel(text):
    # type: (Text) -> Text
    """Escape text for channel name.

    Args:
        text (str): Text for escaped

    Returns:
        str: Escaped text.

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

    ret = cast.text(text)
    if '.' not in ret:
        ret = 'mask_extra.{}'.format(ret)
    ret = ret.replace(' ', '_')
    ret = '{0[0]}{0[1]}{1}'.format(
        ret.partition('.')[:-1], ret.partition('.')[-1].replace('.', '_'))
    ret = ret.encode('ascii', 'replace').decode("ascii")
    return ret


def named_copy(
    n,  # type: nuke.Node
    names_dict,  # type: Dict[Text,Text]
):  # type: (...) -> nuke.Node
    """Create multiple Copy node on demand.

    Args:
        n (nuke.Node): Node as input.
        names_dict (dict[str:str]): A dict with source channel name as key,
            target channel name as value.

    Returns:
        nuke.Node: Output node.
    """

    def _rgba_order(channel):
        # type: (six.text_type) -> six.text_type
        ret = channel
        repl = (('.red', '.0_'), ('.green', '.1_'),
                ('.blue', '.2_'), ('.alpha', '3_'))
        ret = six.moves.reduce(
            lambda text, repl: text.replace(*repl), repl, ret)
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
        for k, v in names_dict.items() if v
    }

    for i, k in enumerate(sorted(names_dict, key=_rgba_order)):
        v = names_dict[k]

        index = i % 4
        if not index:
            n = nuke.nodes.Copy(inputs=[n, n])
        _ = n[cast.binary('from{}'.format(index))].setValue(k)
        add_channel(v)
        _ = n[cast.binary('to{}'.format(index))].setValue(v)
    return n


def split_layers(node):
    # type: (nuke.Node) -> List[nuke.Node]
    """Create Shuffle node for each layers in node @n.  """

    ret = [] # type: List[nuke.Node]

    for layer in nuke.layers(node):
        if layer in ['rgb', 'rgba', 'alpha']:
            continue
        kwargs = {'in': layer,
                  'label': layer}
        try:
            kwargs['postage_stamp'] = node[b'postage_stamp'].value()
        except NameError:
            pass
        n = nuke.nodes.Shuffle(inputs=[node], **kwargs)
        ret.append(n)
    return ret


def shuffle_rgba(node):
    # type: (nuke.Node) -> List[nuke.Node]
    """Create rgba shuffle."""

    channels = ('red', 'green', 'blue', 'alpha')
    ret = [] # type: List[nuke.Node]

    for channel in channels:
        kwargs = {'label': channel}
        for i in channels:
            kwargs[i] = channel
        try:
            kwargs['postage_stamp'] = node[b'postage_stamp'].value()
        except NameError:
            pass
        n = nuke.nodes.Shuffle(inputs=[node], **kwargs)
        ret.append(n)

    return ret


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
    input1_layers = nuke.layers(input1)
    try:
        input_channel = [i for i in (layer, output, 'rgba')
                         if i in input1_layers][0]
    except IndexError:
        raise ValueError('Can not find avaliable layer in input1',
                         input1_layers)

    _ = add_layer(output)
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
