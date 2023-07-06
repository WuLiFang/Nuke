# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import xml.sax.saxutils

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


# spell-checker: word apos

_html_escape_table = {'"': "&quot;", "'": "&apos;"}


def escape_html(s):
    # type: (Text) -> Text
    return xml.sax.saxutils.escape(s, _html_escape_table)
