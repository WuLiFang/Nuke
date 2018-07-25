# -*- coding=UTF-8 -*-
"""Best practice for nuke compositiing.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

from wlf.codectools import get_unicode as u
from wlf.codectools import u_print

from . import channel


def glow_no_mask(temp_channel='mask.a', is_show_result=True):
    """Use width channel on `Glow2` node, instead of mask.  """

    channel.add_channel(temp_channel)
    nodes = nuke.allNodes('Glow2')
    result = [n for n in nodes if _replace_glow_mask(n, temp_channel)]

    if not is_show_result:
        return
    if result:

        nuke.message('将{}个Glow节点的mask更改为了width channel:\n{}'.format(
            len(result), ','.join(u(n.name()) for n in result)
        ).encode('utf-8'))
    else:
        nuke.message('没有发现使用了mask的Glow节点。'.encode('utf-8'))


def _replace_glow_mask(n, temp_channel='mask.a'):
    mask_knob = 'maskChannelMask' if n.input(1) else 'maskChannelInput'
    mask_channel = u(n[mask_knob].value())

    if mask_channel == 'none':
        return False

    copy_node = nuke.nodes.Copy(
        inputs=(n.input(0), n.input(1)), from0=mask_channel, to0=temp_channel)
    copy_node.setXYpos(n.xpos(),
                       n.ypos() - max(copy_node.screenHeight(), 32) - 10)
    width_channel = n['W'].value()
    if width_channel != 'none':
        input0 = nuke.nodes.ChannelMerge(
            inputs=(copy_node, copy_node),
            A=temp_channel,
            operation='in',
            B=width_channel,)
    else:
        input0 = copy_node

    n.setInput(0, input0)
    n.setInput(1, None)
    n['maskChannelMask'].setValue('none')
    n['maskChannelInput'].setValue('none')
    n['W'].setValue(temp_channel)

    u_print('修正Glow节点mask: {}'.format(u(n.name())))
    return True
