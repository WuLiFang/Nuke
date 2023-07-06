# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import nuke

from wulifang._util import cast_str, iteritems

from ._unsafe_set_knob_value import unsafe_set_knob_value

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def try_apply_knob_values(
    node,  # type: nuke.Node
    knob_values,  # type: dict[Text, object]
):
    for knob_name, value in iteritems(knob_values):
        try:
            unsafe_set_knob_value(node[cast_str(knob_name)], value)
        except (AttributeError, NameError, TypeError):
            pass
