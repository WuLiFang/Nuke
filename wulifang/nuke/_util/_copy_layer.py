# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang._util import (
    cast_str,
)
from ._create_node import create_node

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional


def copy_layer(
    dst_node,
    dst_layer,
    src_node,
    src_layer,
):
    # type: (Optional[nuke.Node], Text, Optional[nuke.Node], Text) -> nuke.Node
    if src_node is dst_node and src_layer == dst_layer and src_node:
        # no need to create node.
        return src_node

    nuke.Layer(cast_str(dst_layer), nuke.Layer(cast_str(src_layer)).channels())
    if src_node is dst_node and src_node:
        return create_node(
            "Shuffle",
            "\n".join(
                (
                    "in %s" % (src_layer,),
                    "out %s" % (dst_layer,),
                )
            ),
            inputs=(src_node,),
        )
    return create_node(
        "Merge2",
        "\n".join(
            (
                "operation copy",
                "Achannels %s" % (src_layer,),
                "Bchannels none",
                "output %s" % (dst_layer,),
            )
        ),
        inputs=(dst_node, src_node),
        tile_color=0x9E3C63FF,
        label="%s -> %s" % (src_layer, dst_layer),
    )
