# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none
# PSD 拆层，支持中文图层名。

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text
import nuke
import nukescripts.psd
import wulifang.nuke
from wulifang._util import cast_str, cast_text, iteritems, capture_exception
from wulifang.nuke._util import knob_of, create_node
from wulifang._compat.str import Str




class _Layer:
    def __init__(self):
        self.attrs = {}  # type: dict[Text, Text | float]


def _get_layers(metadata):
    # type: (dict[Str, Str | float]) -> list[_Layer]
    layers = []  # type: list[_Layer]

    for k, v in iteritems(metadata):
        key = cast_text(k)
        if key.startswith("input/psd/layers/"):
            splitKey = key.split("/")
            num = int(splitKey[3])
            attr = splitKey[4]
            try:
                attr += "/" + splitKey[5]
            except:
                pass

            while len(layers) <= num:
                layers.append(_Layer())
            if isinstance(v, Str):
                v = cast_text(v)
            layers[num].attrs[attr] = v

    return layers


def breakout_layers(node, sRGB=True):
    # type: (nuke.Node, bool) -> None

    if not node:
        return

    with nuke.Undo(cast_str("PSD拆层")), capture_exception():
        blendMap = {}  # type: dict[Text,Text]
        blendMap["norm"] = "normal"
        blendMap["scrn"] = "screen"
        blendMap["div "] = "color dodge"
        blendMap["over"] = "overlay"
        blendMap["mul "] = "multiply"
        blendMap["dark"] = "darken"
        blendMap["idiv"] = "color burn"
        blendMap["lbrn"] = "linear burn"
        blendMap["lite"] = "lighten"
        blendMap["lddg"] = "linear dodge"
        blendMap["lgCl"] = "lighter color"
        blendMap["sLit"] = "soft light"
        blendMap["hLit"] = "hard light"
        blendMap["lLit"] = "linear light"
        blendMap["vLit"] = "vivid light"
        blendMap["pLit"] = "pin light"
        blendMap["hMix"] = "hard mix"
        blendMap["diff"] = "difference"
        blendMap["smud"] = "exclusion"
        blendMap["fsub"] = "subtract"
        blendMap["fdiv"] = "divide"
        blendMap["hue "] = "hue"
        blendMap["sat "] = "saturation"
        blendMap["colr"] = "color"
        blendMap["lum "] = "luminosity"

        metaData = node.metadata()
        layers = _get_layers(metaData)

        x_spacing = 80

        dot_x_fudge = 34
        dot_y_fudge = 4

        backdrop_x_fudge = -(x_spacing // 2) + 10
        backdrop_y_fudge = -40

        spacing = 70

        x = node.xpos()
        y = node.ypos()
        curY = y + spacing * 2

        if not sRGB:
            colorSpace = nuke.nodes.Colorspace()
            knob_of(colorSpace, "channels", nuke.ChannelMask_Knob).setValue(
                cast_str("all")
            )
            knob_of(colorSpace, "colorspace_out", nuke.Enumeration_Knob).setValue(
                cast_str("all")
            )
            colorSpace.setInput(0, node)
            colorSpace.setXYpos(x, curY)

            inputNode = colorSpace
        else:
            inputNode = node

        curX = x
        curY = y + spacing * 2
        topY = curY

        lastLayer = None

        i = 0

        for l in layers:

            try:
                v = l.attrs["divider/type"]
                if isinstance(v, (int, float)) and v > 0:
                    ## hidden divider or start of group
                    continue
            except:
                pass

            i = i + 1
            if i > 100:
                nuke.message(cast_str("Too many layers, stopping at layer 100."))
                break

            name = cast_text(l.attrs["nukeName"])

            curY = topY

            if i % 2:
                tileColor = 2829621248
            else:
                tileColor = 1751668736

            backdrop = create_node(
                "BackdropNode",
                "note_font_size 18",
                tile_color=tileColor,
                label=cast_text(l.attrs["name"]),
            )
            backdrop.setXYpos(curX + backdrop_x_fudge, curY + backdrop_y_fudge)

            curY += spacing // 2

            dot = nuke.nodes.Dot()
            dot.setInput(0, inputNode)
            dot.setXYpos(curX + dot_x_fudge, curY + dot_y_fudge)
            curY += spacing

            inputNode = dot

            ## if no 'alpha' assume alpha of 1
            alpha_chan = "alpha"
            if not cast_str(name + ".alpha") in inputNode.channels():
                alpha_chan = "white"
            shuffle = create_node(
                "Shuffle",
                """\
in %s
in2 none
red red
green green
blue blue
alpha %s
black red2
white green2
red2 blue2
green2 alpha2
out rgba
out2 none
"""
                % (name, alpha_chan),
                inputs=(inputNode,),
                label=name,
                xpos=curX,
                ypos=curY,
            )

            curY += spacing

            crop = create_node(
                "Crop",
                """\
box {%f %f %f %f}
                """
                % (l.attrs["x"], l.attrs["y"], l.attrs["r"], l.attrs["t"]),
                inputs=(shuffle,),
                xpos=curX,
                ypos=curY,
            )

            curY += spacing * 2

            layer = crop

            try:
                operation = blendMap[cast_text(l.attrs["blendmode"])]
            except:
                print("unknown blending mode %s" % (l.attrs["blendmode"],))
                operation = "normal"

            if lastLayer:
                psdMerge = create_node(
                    "PSDMerge",
                    """\
operation %s
mix %f
"""
                    % (operation, float(l.attrs["opacity"]) / 255.0),
                    inputs=(lastLayer, layer),
                    xpos=curX,
                    ypos=curY,
                )
                knob_of(psdMerge, "sRGB", nuke.Boolean_Knob).setValue(sRGB)
                try:
                    if l.attrs["mask/disable"] != True:
                        knob_of(
                            psdMerge, "maskChannelInput", nuke.Channel_Knob
                        ).setValue(cast_str(name + ".mask"))
                        if l.attrs["mask/invert"] == True:
                            knob_of(
                                psdMerge, "invert_mask", nuke.Boolean_Knob
                            ).setValue(True)
                except:
                    pass
                lastLayer = psdMerge
            else:
                dot = nuke.nodes.Dot()
                dot.setInput(0, layer)
                dot.setXYpos(curX + dot_x_fudge, curY + dot_y_fudge)
                lastLayer = dot

            curY += spacing

            knob_of(backdrop, "bdwidth", nuke.Array_Knob).setValue(
                x_spacing * 2 + backdrop_x_fudge * 2 + 50
            )
            knob_of(backdrop, "bdheight", nuke.Array_Knob).setValue(
                (curY - backdrop.ypos()) - backdrop_y_fudge - 50
            )

            curY += spacing

            curX = curX + x_spacing * 2 + backdrop_x_fudge * 2 + 50

        if not sRGB and lastLayer:
            create_node(
                "Colorspace",
                """\
channels all
colorspace_in sRGB
    """,
                inputs=(lastLayer,),
                xpos=lastLayer.xpos(),
                ypos=lastLayer.ypos() + 2 * spacing,
            )


def init_gui():
    raw = nukescripts.psd.breakoutLayers

    def cleanup():
        nukescripts.psd.breakoutLayers = raw

    wulifang.cleanup.add(cleanup)
    nukescripts.psd.breakoutLayers = breakout_layers
