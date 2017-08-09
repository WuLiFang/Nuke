# -*- coding=UTF-8 -*-
import random

import nuke

__version__ = '0.1.0'


def orgnize_nodes(nodes):
    """orgnize node posion and add backdrops.  """
    # TODO
    meta_input_dict = {}
    for n in nodes:
        meta_input = n.metadata('input/filename')
        if meta_input:
            meta_input_dict.setdefault(meta_input, [])
            meta_input_dict[meta_input].append(n)

    for meta_input, nodes in meta_input_dict.items():
        map(nuke.autoplace, nodes)
        n = create_backdrop(nodes)


def is_node_inside(node, backdropNode):
    """Returns true if node geometry is inside backdropNode otherwise returns false"""
    topLeftNode = [node.xpos(), node.ypos()]
    topLeftBackDrop = [backdropNode.xpos(), backdropNode.ypos()]
    bottomRightNode = [node.xpos() + node.screenWidth(),
                       node.ypos() + node.screenHeight()]
    bottomRightBackdrop = [backdropNode.xpos(
    ) + backdropNode.screenWidth(), backdropNode.ypos() + backdropNode.screenHeight()]

    topLeft = (topLeftNode[0] >= topLeftBackDrop[0]) and (
        topLeftNode[1] >= topLeftBackDrop[1])
    bottomRight = (bottomRightNode[0] <= bottomRightBackdrop[0]) and (
        bottomRightNode[1] <= bottomRightBackdrop[1])

    return topLeft and bottomRight


def autoplace(nodes):
    print(nodes)
    map(nuke.autoplace, nodes)


def create_backdrop(nodes, autoplace_nodes=False):
    ''' 
    Automatically puts a backdrop behind the selected nodes. 

    The backdrop will be just big enough to fit all the select nodes in, with room 
    at the top for some text in a large font. 
    '''
    if autoplace_nodes:
        autoplace(nodes)
    if not nodes:
        return nuke.nodes.BackdropNode()

    # Calculate bounds for the backdrop node.
    bdX = min([node.xpos() for node in nodes])
    bdY = min([node.ypos() for node in nodes])
    bdW = max([node.xpos() + node.screenWidth() for node in nodes]) - bdX
    bdH = max([node.ypos() + node.screenHeight() for node in nodes]) - bdY

    zOrder = 0
    selectedBackdropNodes = nuke.selectedNodes("BackdropNode")
    # if there are backdropNodes selected put the new one immediately behind the farthest one
    if len(selectedBackdropNodes):
        zOrder = min([node.knob("z_order").value()
                      for node in selectedBackdropNodes]) - 1
    else:
        # otherwise (no backdrop in selection) find the nearest backdrop if exists and set the new one in front of it
        nonSelectedBackdropNodes = nuke.allNodes("BackdropNode")
    for nonBackdrop in nodes:
        for backdrop in nonSelectedBackdropNodes:
            if is_node_inside(nonBackdrop, backdrop):
                zOrder = max(zOrder, backdrop.knob("z_order").value() + 1)

    # Expand the bounds to leave a little border. Elements are offsets for left, top, right and bottom edges respectively
    left, top, right, bottom = (-10, -80, 10, 10)
    bdX += left
    bdY += top
    bdW += (right - left)
    bdH += (bottom - top)

    n = nuke.nodes.BackdropNode(xpos=bdX,
                                bdwidth=bdW,
                                ypos=bdY,
                                bdheight=bdH,
                                tile_color=int(
                                    (random.random() * (16 - 10))) + 10,
                                note_font_size=42,
                                z_order=zOrder)

    return n
