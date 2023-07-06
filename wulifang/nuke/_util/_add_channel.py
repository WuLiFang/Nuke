# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang._util import cast_str

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def _sanitize_ascii(s):
    # type: (Text) -> Text
    return s.encode("ascii", "replace").decode("ascii")


def _channel_from_input(
    s,  # type: Text
):
    """Escape text for channel name.

    Args:
        text (str): Text for escaped

    Returns:
        str: Escaped text.

    Example:
        >>> _channel_from_input('apple')
        'other.apple'
        >>> _channel_from_input('tree.apple')
        'tree.apple'
        >>> _channel_from_input('tree.apple.leaf')
        'tree.apple_leaf'
        >>> _channel_from_input('tree.apple.leaf.根')
        'tree.apple_leaf_?'
    """


    s = _sanitize_ascii(s).replace(" ", "_")
    if "." not in s:
        # `other` is nuke default layer
        s = "other.%s" % (s,)

    layer, _, channel = s.partition(".")
    channel = channel.replace(".", "_")
    return layer, channel


def add_channel(
    name,  # type: Text
):  # type: (...) -> ...
    """Add a channel from `{layer}.{channel}` format string.

    Args:
        name (str): Channel name.
    """

    layer, channel = _channel_from_input(name)
    nuke.Layer(cast_str(layer), [cast_str(channel)])
    return "%s.%s" % (layer, channel)
