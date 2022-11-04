# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

from ._timezone import TZ_UTC
from datetime import datetime

NULL_TIME = datetime.fromtimestamp(0, TZ_UTC)
