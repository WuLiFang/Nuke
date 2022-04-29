# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import absolute_import, division, print_function, unicode_literals


TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text

from wulifang.vendor import cgtwq
from wulifang.vendor.cgtwq.helper.wlf import get_entry_by_file


def entry_from_shot(shot, pipeline="合成"):
    # type: (Text, Text) -> cgtwq.Entry
    """Get task entry from shot name.

    Args:
        shot (str): Shot name.
        pipeline (str, optional): Defaults to '合成'. Pipline name.
    """

    return get_entry_by_file(shot, pipeline)
