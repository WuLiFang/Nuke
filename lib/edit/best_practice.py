# -*- coding=UTF-8 -*-
"""Best practice for nuke compositing.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

import cast_unknown as cast

from . import channel

import logging
LOGGER = logging.getLogger(__name__)


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def glow_no_mask(
    temp_channel='mask.a',  # type: Text
    is_show_result=True,  # type: bool
):  # type: (...) -> None
    """Use width channel on `Glow2` node, instead of mask.  """

    channel.add_channel(temp_channel)
    nodes = nuke.allNodes(b'Glow2')
    result = [n for n in nodes if _replace_glow_mask(n, temp_channel)]

    if not is_show_result:
        return
    if result:

        nuke.message('将{}个Glow节点的mask更改为了width channel:\n{}'.format(
            len(result), ','.join(cast.text(n.name()) for n in result)
        ).encode('utf-8'))
    else:
        nuke.message('没有发现使用了mask的Glow节点。'.encode('utf-8'))


def _replace_glow_mask(
    n,  # type: nuke.Node
    temp_channel='mask.a',  # type: Text
):
    mask_knob = 'maskChannelMask' if n.input(1) else 'maskChannelInput'
    mask_channel = cast.text(n[cast.binary(mask_knob)].value())

    if mask_channel == 'none':
        return False

    copy_node = nuke.nodes.Copy(
        inputs=(n.input(0), n.input(1)), from0=mask_channel, to0=temp_channel)
    copy_node.setXYpos(n.xpos(),
                       n.ypos() - max(copy_node.screenHeight(), 32) - 10)
    width_channel = n[b'W'].value()
    if width_channel != 'none':
        input0 = nuke.nodes.ChannelMerge(
            inputs=(copy_node, copy_node),
            A=temp_channel,
            operation='in',
            B=width_channel,)
    else:
        input0 = copy_node

    _ = n.setInput(0, input0)
    _ = n.setInput(1, None)
    _ = n[b'maskChannelMask'].setValue('none')
    _ = n[b'maskChannelInput'].setValue('none')
    _ = n[b'W'].setValue(temp_channel)

    LOGGER.info('修正Glow节点mask: {}'.format(cast.text(n.name())))
    return True
