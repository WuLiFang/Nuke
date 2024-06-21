# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Iterator

from wulifang._util import lazy_getter, cast_text

import nuke
import os


def _ext_by_plugin(__dir):
    # type: (Text) -> Iterator[Text]
    try:
        files = os.listdir(__dir)
    except OSError:
        return

    for file in files:
        s = file.lower()
        try:
            index = s.index("writer")
        except ValueError:
            continue
        yield ".%s" % (s[:index],)


@lazy_getter
def _supported_ext():
    # type: () -> set[Text]

    v = set(_ext_by_plugin(os.path.join(cast_text(nuke.EXE_PATH), "../plugins")))
    v.add(".mov")
    v.add(".exr")
    return v


def supports_write(__ext):
    # type: (Text) -> bool
    if not __ext:
        return False
    return __ext.lower() in _supported_ext()
