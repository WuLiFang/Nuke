# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang.nuke._util import (
    create_node,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Iterator


def split(_node):
    # type: (nuke.Node) -> Iterator[nuke.Node]
    """Create Shuffle node for each layers in node @n."""

    for channel in ("red", "green", "blue", "alpha"):
        yield create_node(
            "Shuffle",
            """\
red %s
green %s
blue %s
alpha %s
postage_stamp true"""
            % (channel, channel, channel, channel),
            inputs=[_node],
            label=channel,
        )
