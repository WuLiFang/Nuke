# -*- coding=UTF-8 -*-

import nuke


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any


def cast_str(v):
    # type: (str) -> Any
    return v


nuke.pluginAddPath(cast_str("Tangent_Space_Normals"))
