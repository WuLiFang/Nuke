# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Union, Callable

import re

# reference https://github.com/parshap/node-sanitize-filename/blob/master/index.js
_PATTERN = re.compile(
    r'[/?<>\\:\*|"\x00-\x1f\x80-\x9f]|^\.+$|[\. ]+$|(?i)^(con|prn|aux|nul|com[0-9]|lpt[0-9])(\..*)?$'
)


def sanitize_filename(s, repl="�"):
    # type: (Text, Union[Text, Callable[[Text], Text]]) -> Text
    return _PATTERN.sub(repl, s)  # type: ignore
