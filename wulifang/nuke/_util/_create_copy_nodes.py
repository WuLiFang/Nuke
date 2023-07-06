# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang.vendor import six
from wulifang._util import iteritems, cast_str

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text

from ._add_channel import add_channel

# For short version channel name.
_TO_ALIAS = {
    "r": "rgba.red",
    "g": "rgba.green",
    "b": "rgba.blue",
    "a": "rgba.alpha",
    "red": "rgba.red",
    "green": "rgba.green",
    "blue": "rgba.blue",
    "alpha": "rgba.alpha",
}


def create_copy_nodes(
    node,  # type: nuke.Node
    channels,  # type: dict[Text, Text]
):  # type: (...) -> nuke.Node
    """Create multiple Copy node on demand.

    Args:
        node: Input node.
        names: {to_channel: from_channel}

    Returns:
        nuke.Node: Output node.
    """

    def order(channel):
        # type: (Text) -> Text
        ret = channel
        repl = ((".red", ".0_"), (".green", ".1_"), (".blue", ".2_"), (".alpha", "3_"))
        ret = six.moves.reduce(lambda text, repl: text.replace(*repl), repl, ret)  # type: ignore
        return ret

    # normalize input
    channels = {
        add_channel(_TO_ALIAS.get(k, k)): add_channel(v)
        for k, v in iteritems(channels)
        if v
    }
    n = node
    for i, from_ in enumerate(sorted(channels, key=order)):
        to = channels[from_]
        num = i % 4
        if not n or num == 0:
            n = nuke.nodes.Copy(inputs=[n, n])
        n[cast_str("from{}".format(num))].setValue(from_)
        n[cast_str("to{}".format(num))].setValue(to)
    return n
