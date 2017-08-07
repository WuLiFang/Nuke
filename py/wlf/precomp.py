# -*- coding=UTF-8 -*-
"""Comp multi pass to beauty."""
import nuke
from wlf.files import get_layer, REDSHIFT_LAYERS
from wlf.edit import add_layer
__version__ = '0.1.3'


def redshift(nodes):
    """Precomp reshift spereated footage."""
    task = nuke.ProgressTask('Redshift???')

    source = {get_layer(nuke.filename(input1)): input1 for input1 in nodes}
    assert source.get('DiffuseLighting'), '没有DiffuseLighting层'
    n = source.get('DiffuseLighting')

    def _layer_order(name):
        try:
            return '{:05d}_{}'.format(REDSHIFT_LAYERS.index(name), name)
        except ValueError:
            return '~{}'.format(name)
    layers = sorted((i for i in source.keys() if i), key=_layer_order)
    for index, layer in enumerate(layers):
        task.setMessage(layer)
        task.setProgress(index * 100 // len(layers))
        input1 = source.get(layer)
        if not (layer and input1):
            continue

        # plus layer
        if layer in ('SSS', 'Reflections', 'Refractions', 'SpecularLighting',
                     'GI', 'Emission', 'Caustics'):
            n = nuke.nodes.Merge2(
                inputs=[n, input1], operation='plus', label=layer)
        # depth layer
        if layer in ('Z'):
            add_layer('depth')
            n = nuke.nodes.Copy(
                inputs=[n, input1], from0='depth.Z', to0='depth.Z', label='depth')
        # copy layer
        if layer in ('MotionVectors', 'BumpNormals', 'P', 'DiffuseFilter', 'TransTint'):
            add_layer(layer)
            n = nuke.nodes.Merge2(
                inputs=[n, input1], operation='copy',
                Achannels='rgba', Bchannels='none', output=layer, label=layer)
        if layer.startswith('PuzzleMatte'):
            add_layer(layer)
            n = nuke.nodes.Merge2(
                inputs=[n, input1], operation='copy',
                Achannels='rgba', Bchannels='none', output=layer, label=layer)
    return n


def arnold():
    """This function is copyed from cgspread."""

    # set a ordered list of input layer
    layerlist = ['indirect_diffuse', 'direct_diffuse',
                 'indirect_specular', 'direct_specular', 'reflection',
                 'refraction',
                 'AO', 'depth', 'MV', 'alpha']
    # gradelayers = ['indirect_diffuse',
    #  'direct_diffuse',
    #  'indirect_specular',
    #  'direct_specular',
    #  'reflection',
    #                'refraction',
    #                'AO']
    # Get The Layers Of Selected Read Node

    orderedmerge = []

    read_node = nuke.selectedNode()
    layers = nuke.layers(read_node)

    for i in layerlist:
        for n in layers:
            if i == n:
                orderedmerge.append(i)

    for merge in orderedmerge:
        for layer in layers:
            if layer == merge:
                layers.remove(layer)

    layers.remove(u'rgba')
    layers.remove(u'rgb')
    orderedshow = layers

    ################Create Shuffle########################################

    xpos = read_node['xpos'].getValue()
    ypos = read_node['ypos'].getValue()

    shufflegroup = []
    gradegroup = []
    dot_ygroup = []
    mergegroup = []
    for k in orderedmerge:
        shuffle = nuke.nodes.Shuffle(
            name=k, postage_stamp=1, note_font_size=25)
        shuffle.setInput(0, read_node)
        shuffle.Knob('in').setValue(k)
        num = int(orderedmerge.index(k))
        shuffle.setXYpos(int(xpos + 150 * num), int(ypos + 250))
        shuffle_x = shuffle['xpos'].getValue()
        shuffle_y = shuffle['ypos'].getValue()
        shufflegroup.append(shuffle)

        ###Create Grade###
        if num < 7:
            gradenode = nuke.nodes.Grade(name=k, note_font_size=15)
            gradenode.setInput(0, shuffle)
            gradegroup.append(gradenode)
        else:
            pass

        ###Create Dot#####

        if num >= 1 and num < 7:
            dot = nuke.nodes.Dot(name=k, label=k, note_font_size=25)
            dot.setInput(0, gradenode)
            dot.setXYpos(int(shuffle_x + 34), int(shuffle_y + 180 * num))
            # dotX = dot['xpos'].getValue()
            dot_y = dot['ypos'].getValue()
            dot_ygroup.append(dot_y)

        elif num > 6:
            dot = nuke.nodes.Dot(name=k, label=k, note_font_size=25)
            dot.setInput(0, shuffle)
            dot.setXYpos(int(shuffle_x + 34), int(shuffle_y + 180 * num))
            # dotX = dot['xpos'].getValue()
            dot_y = dot['ypos'].getValue()
            dot_ygroup.append(dot_y)

        ###Create Merge####

        if num < 1:
            pass
        elif num > 0 and num < 2:
            merge = nuke.nodes.Merge(name=k,
                                     operation='plus',
                                     mix=1,
                                     inputs=[gradegroup[0], dot],
                                     note_font_size=15)
            merge.setXYpos(int(xpos), int(dot_y - 6))
            mergegroup.append(merge)
        elif num > 1 and num < 6:
            merge = nuke.nodes.Merge(name=k,
                                     inputs=[mergegroup[num - 2], dot],
                                     operation='plus', mix=1,
                                     note_font_size=15)
            mergegroup.append(merge)
            merge.setXYpos(int(xpos), int(dot_y - 6))
        elif num > 5 and num < 7:
            merge = nuke.nodes.Merge(name=k,
                                     inputs=[mergegroup[num - 2], dot],
                                     operation='multiply',
                                     mix=0.15,
                                     note_font_size=15)
            mergegroup.append(merge)
            merge.setXYpos(int(xpos), int(dot_y - 6))
        elif num > 6 and num < 8:
            copy = nuke.nodes.Copy(name=k,
                                   inputs=[mergegroup[num - 2], dot],
                                   from0='rgba.red',
                                   to0='depth.Z',
                                   note_font_size=15)
            mergegroup.append(copy)
            copy.setXYpos(int(xpos), int(dot_y - 14))
        elif num > 7 and num < 9:
            copy = nuke.nodes.Copy(name=k,
                                   inputs=[mergegroup[num - 2], dot],
                                   from0='rgba.red',
                                   to0='MV.red',
                                   from1='rgba.green',
                                   to1='MV.green',
                                   note_font_size=15)
            mergegroup.append(copy)
            copy.setXYpos(int(xpos), int(dot_y - 26))
        elif num > 8 and num < 10:
            copy = nuke.nodes.Copy(name=k,
                                   inputs=[mergegroup[num - 2], dot],
                                   from0='rgba.red',
                                   to0='rgba.alpha',
                                   note_font_size=15)
            mergegroup.append(copy)
            copy.setXYpos(int(xpos), int(dot_y - 14))
            ###Create show Layers####

    for element in orderedshow:
        num += 1
        shuffle = nuke.nodes.Shuffle(
            name=element, postage_stamp=1, note_font_size=25)
        shuffle.setInput(0, read_node)
        shuffle.Knob('in').setValue(element)
        shuffle.setXYpos(int(xpos + 150 * num), int(ypos + 250))

    nuke.connectViewer(0, mergegroup[-1])
