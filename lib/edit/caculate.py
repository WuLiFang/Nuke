# -*- coding=UTF-8 -*-
"""Caculate image value.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke


def get_min_max(src_node, channel='depth.Z'):
    '''
    Return the min and max values of a given node's image as a tuple

    args:
       src_node  - node to analyse
       channels  - channels to analyse.
            This can either be a channel or layer name
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
