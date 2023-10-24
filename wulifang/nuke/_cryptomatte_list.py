# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import (
        Text,
        Sequence,
        Self,
    )


import re
import csv

import nuke

from wulifang.nuke._util import knob_of
from wulifang._util import cast_text, cast_str


class CryptomatteList:
    # https://github.com/Psyop/Cryptomatte/blob/968d5e4b6171e29ba5f89d554117132a164e747e/nuke/cryptomatte_utilities.py#L1221

    _WILDCARDS_PATTERN = re.compile(r"(?<!\\)([*?\[\]])")

    def __init__(self, __raw):
        # type: (Sequence[Text]) -> None
        self.raw = __raw

    def has_wildcard(self):
        return any(self._WILDCARDS_PATTERN.search(i) for i in self.raw)

    def to_csv(self):
        # type: () -> Text
        cleaned_items = []  # type: list[Text]
        need_escape_chars = '"\\'
        need_quotes_characters = " ,"

        for item in self.raw:
            need_escape = any(x in item for x in need_escape_chars)
            need_quotes = need_escape or any(x in item for x in need_quotes_characters)

            cleaned = None
            if need_escape:
                cleaned = ""
                for char in item:
                    if char in need_escape_chars:
                        cleaned += "\\%s" % char
                    else:
                        cleaned += char
            else:
                cleaned = item
            if need_quotes:
                cleaned_items.append('"%s"' % cleaned)
            else:
                cleaned_items.append(cleaned)
        return ", ".join(cleaned_items)

    def to_cryptomatte(self, __node):
        # type: (nuke.Node) -> None
        assert (
            cast_text(__node.Class()) == "Cryptomatte"
        ), "should be a Cryptomatte node, got %s " % (cast_text(__node.Class()),)
        s = self.to_csv()
        s = s.replace("[", "\\[").replace("]", "\\]").replace('\\"', '\\\\"')
        knob_of(__node, "matteList", nuke.String_Knob).setValue(cast_str(s))

    @classmethod
    def from_csv(cls, __s):
        # type: (Text) -> Self
        reader = csv.reader(
            (__s,),
            quotechar=cast_str('"'), # type: ignore
            delimiter=cast_str(","), # type: ignore
            escapechar=cast_str("\\"), # type: ignore
            doublequote=False,
            quoting=csv.QUOTE_ALL,
            skipinitialspace=True,
        )
        raw = []  # type: list[Text]
        for row in reader:
            raw += row
        return cls(raw)

    @classmethod
    def from_cryptomatte(cls, __node):
        # type: (nuke.Node) -> Self
        """Converts a nuke string to one that can be consumed by CSV
        getvalue will have stripped escape characters, so we need to restore them.
        Also need to avoid double-escaping "
        """
        assert (
            cast_text(__node.Class()) == "Cryptomatte"
        ), "should be a Cryptomatte node, got %s " % (cast_text(__node.Class()),)
        s = cast_text(knob_of(__node, "matteList", nuke.String_Knob).getValue())
        return cls.from_csv(s.replace("\\", "\\\\").replace('\\\\"', '\\"'))
