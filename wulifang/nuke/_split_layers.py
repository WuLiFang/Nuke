# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang._util import (
    cast_text,
)
from wulifang.nuke._util import (
    create_node,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterator


def split(_node):
    # type: (nuke.Node) -> Iterator[nuke.Node]
    """Create Shuffle node for each layers in node @n."""

    for layer in nuke.layers(_node):
        layer = cast_text(layer)
        if layer in ("rgb", "rgba", "alpha"):
            continue
        yield create_node(
            "Shuffle",
            """\
in %s
postage_stamp true"""
            % (layer,),
            inputs=[_node],
            label=layer,
        )
