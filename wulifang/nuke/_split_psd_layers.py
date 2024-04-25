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


# spell-checker: word lbrn lddg smud fsub fdiv colr
_BLEND_MAP = {
    "norm": "normal",
    "scrn": "screen",
    "div ": "color dodge",
    "over": "overlay",
    "mul ": "multiply",
    "dark": "darken",
    "idiv": "color burn",
    "lbrn": "linear burn",
    "lite": "lighten",
    "lddg": "linear dodge",
    "lgCl": "lighter color",
    "sLit": "soft light",
    "hLit": "hard light",
    "lLit": "linear light",
    "vLit": "vivid light",
    "pLit": "pin light",
    "hMix": "hard mix",
    "diff": "difference",
    "smud": "exclusion",
    "fsub": "subtract",
    "fdiv": "divide",
    "hue ": "hue",
    "sat ": "saturation",
    "colr": "color",
    "lum ": "luminosity",
}

_CHUNK_SIZE = 32


def split(__node, s_rgb=True):
    # type: (nuke.Node, bool) -> None
    with nuke.Undo(cast_str("PSD拆层")), capture_exception():
        metaData = __node.metadata()
        layers = _get_layers(metaData)

        x_spacing = 80

        dot_x_fudge = 34
        dot_y_fudge = 4

        backdrop_x_fudge = -(x_spacing // 2) + 10
        backdrop_y_fudge = -40

        spacing = 70

        x0 = __node.xpos()
        y0 = __node.ypos()
        y = y0 + spacing * 2
        x = x0
        top_y = y
        last_layer = None

        if not s_rgb:
            input_node = create_node(
                "Colorspace",
                "channels all\ncolorspace_out all",
                inputs=(__node,),
                xpos=x0,
                ypos=y,
            )
        else:
            input_node = __node
        i = 0

        def filtered_layers():
            for i in layers:
                # hidden divider or start of group
                try:
                    if int(i.attrs["divider/type"]) > 0:
                        continue
                except (ValueError, KeyError):
                    pass
                yield i

        for i, l in enumerate(
            filtered_layers(),
        ):
            if (
                i > 0
                and i % _CHUNK_SIZE == 0
                and not nuke.ask(cast_str("已经拆分出了 %d 个图层，继续？" % (i,)))
            ):
                return

            name = cast_text(l.attrs["nukeName"])

            y = top_y
            backdrop = create_node(
                "BackdropNode",
                "note_font_size 18",
                tile_color=0xA8A89800 if i % 2 else 0x68685800,
                label=cast_text(l.attrs["name"]),
                xpos=x + backdrop_x_fudge,
                ypos=y + backdrop_y_fudge,
            )

            y += spacing // 2

            dot = nuke.nodes.Dot()
            dot.setInput(0, input_node)
            dot.setXYpos(x + dot_x_fudge, y + dot_y_fudge)
            y += spacing

            input_node = dot

            # if no 'alpha' assume alpha of 1
            alpha_chan = "alpha"
            if not cast_str(name + ".alpha") in input_node.channels():
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
                inputs=(input_node,),
                label=name,
                xpos=x,
                ypos=y,
            )

            y += spacing

            crop = create_node(
                "Crop",
                """\
box {%f %f %f %f}
                """
                % (l.attrs["x"], l.attrs["y"], l.attrs["r"], l.attrs["t"]),
                inputs=(shuffle,),
                xpos=x,
                ypos=y,
            )

            y += spacing * 2

            layer = crop

            # spell-checker: word blendmode
            try:
                operation = _BLEND_MAP[cast_text(l.attrs["blendmode"])]
            except KeyError:
                wulifang.message.error(
                    "unknown blending mode %s" % (l.attrs["blendmode"],)
                )
                operation = "normal"

            if last_layer:
                psdMerge = create_node(
                    "PSDMerge",
                    """\
operation %s
mix %f
"""
                    % (operation, float(l.attrs["opacity"]) / 255.0),
                    inputs=(last_layer, layer),
                    xpos=x,
                    ypos=y,
                )
                knob_of(psdMerge, "sRGB", nuke.Boolean_Knob).setValue(s_rgb)
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
                last_layer = psdMerge
            else:
                last_layer = create_node(
                    "Dot",
                    inputs=(layer,),
                    xpos=x + dot_x_fudge,
                    ypos=y + dot_y_fudge,
                )

            y += spacing

            # spell-checker: word bdwidth bdheight
            knob_of(backdrop, "bdwidth", nuke.Array_Knob).setValue(
                x_spacing * 2 + backdrop_x_fudge * 2 + 50
            )
            knob_of(backdrop, "bdheight", nuke.Array_Knob).setValue(
                (y - backdrop.ypos()) - backdrop_y_fudge - 50
            )

            y += spacing

            x = x + x_spacing * 2 + backdrop_x_fudge * 2 + 50

        if not s_rgb and last_layer:
            create_node(
                "Colorspace",
                """\
channels all
colorspace_in sRGB
    """,
                inputs=(last_layer,),
                xpos=last_layer.xpos(),
                ypos=last_layer.ypos() + 2 * spacing,
            )


def _breakout_layers_impl(node, sRGB=True):
    # type: (nuke.Node, bool) -> None
    if not node:
        return
    split(node, s_rgb=sRGB)


def init_gui():
    raw = nukescripts.psd.breakoutLayers

    def cleanup():
        nukescripts.psd.breakoutLayers = raw

    wulifang.cleanup.add(cleanup)
    nukescripts.psd.breakoutLayers = _breakout_layers_impl
