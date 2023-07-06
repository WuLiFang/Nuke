# -*- coding: UTF-8 -*-
"""Nuke init file.  """
import nuke

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any


def cast_str(v):
    # type: (str) -> Any
    return v


nuke.pluginAddPath(cast_str("wulifang/nuke/_startup"))
if nuke.GUI:
    nuke.pluginAddPath(cast_str("assets/icons"))
    nuke.pluginAddPath(cast_str("assets/third_party/icons"))
