# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import re
import os

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Sequence


def layer_from_filename(s, accept=()):
    # type: (Text, Sequence[Text]) -> Text
    if not s:
        return ""

    name, _ = os.path.splitext(os.path.basename(s))
    for layer in accept:
        match = re.search(r"\b(%s)\d*\b" % (re.escape(layer),), name)
        if match:
            return match.group(1)
    return ""
