# -*- coding=UTF-8 -*-

import nuke


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any


def cast_str(v):
    # type: (str) -> Any
    return v


nuke.pluginAddPath(cast_str("3D"))
nuke.pluginAddPath(cast_str("Channel"))
nuke.pluginAddPath(cast_str("Color"))
nuke.pluginAddPath(cast_str("Deep"))
nuke.pluginAddPath(cast_str("Draw"))
nuke.pluginAddPath(cast_str("Edge"))
nuke.pluginAddPath(cast_str("Filter"))
nuke.pluginAddPath(cast_str("Image"))
nuke.pluginAddPath(cast_str("Keyer"))
nuke.pluginAddPath(cast_str("Lighting"))
nuke.pluginAddPath(cast_str("Merge"))
nuke.pluginAddPath(cast_str("Obsolete"))
nuke.pluginAddPath(cast_str("Particle"))
nuke.pluginAddPath(cast_str("Transform"))
