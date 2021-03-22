# -*- coding: UTF-8 -*-
"""Edit existed content in workfile."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import best_practice, match_drop_frame
from .caculate import get_max, get_min_max
from .channel import (add_channel, add_layer, copy_layer, escape_for_channel,
                      named_copy, shuffle_rgba, split_layers)
from .cleanup import delete_unused_nodes
from .color import set_random_glcolor
from .core import (all_flags, clear_selection, insert_node, replace_node,
                   set_knobs, transfer_flags)
from .gizmo import all_gizmo_to_group, gizmo_to_group
from .read import (dialog_set_framerange, reload_all_read_node,
                   remove_duplicated_read, replace_sequence, set_framerange,
                   use_relative_path)
from .viewer import CurrentViewer

__all__ = [
    "best_practice",
    "match_drop_frame",
    "get_max",
    "get_min_max",
    "add_channel",
    "add_layer",
    "copy_layer",
    "escape_for_channel",
    "named_copy",
    "shuffle_rgba",
    "split_layers",
    "delete_unused_nodes",
    "set_random_glcolor",
    "all_flags",
    "clear_selection",
    "insert_node",
    "replace_node",
    "set_knobs",
    "transfer_flags",
    "all_gizmo_to_group",
    "gizmo_to_group",
    "dialog_set_framerange",
    "reload_all_read_node",
    "remove_duplicated_read",
    "replace_sequence",
    "set_framerange",
    "use_relative_path",
    "CurrentViewer",
]
