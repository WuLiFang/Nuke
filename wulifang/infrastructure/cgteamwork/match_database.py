# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Iterator


from wulifang.vendor.cgtwq import desktop as cgtw, F


from wulifang._util import cast_text


def _possible_prefix(client):
    # type: (cgtw.Client) -> Iterator[tuple[Text,Text]]
    for code, database, prefix in client.table(
        "public", "project", "info", filter_by=F("project.status").equal("Active")
    ).rows("project.entity", "project.database", "project.description"):
        yield code.lower() + "_", database
        yield prefix.lower(), database


def match_database(client, name):
    # type: (cgtw.Client,Text) -> Iterator[Text]

    s = (cast_text(name)).lower()
    for prefix, database in _possible_prefix(client):
        if prefix and s.startswith(prefix):
            yield database
