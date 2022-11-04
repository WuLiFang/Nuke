# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional

from datetime import datetime, timedelta, tzinfo


class FixedTimezone(tzinfo):
    def __init__(self, name, utcoffset):
        # type: (Text, timedelta) -> None
        self._name = name
        self._utcoffset = utcoffset

    def tzname(self, dt):
        # type: (Optional[datetime]) -> Text
        return self._name

    def utcoffset(self, dt):
        # type: (Optional[datetime]) -> timedelta
        return self._utcoffset

    def dst(self, dt):
        # type: (Optional[datetime]) -> timedelta
        return timedelta()


TZ_UTC = FixedTimezone("UTC", timedelta())
TZ_CHINA = FixedTimezone("UTC+8", timedelta(hours=8))
