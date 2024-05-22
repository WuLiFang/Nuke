# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text

import io
import tempfile

import base64
import os
import atexit
from wulifang.vendor.six.moves import urllib_parse

_URL_MAX_BYTES = 2083


def create_html_url(body, accept_scheme=()):
    # type: (Text, tuple[Text, ...]) -> Text
    if "data:" in accept_scheme:
        data_url = "data:text/html;charset=utf-8;base64,%s" % (
            base64.b64encode(body.encode("utf-8")),
        )
        if len(data_url) <= _URL_MAX_BYTES:
            return data_url

    fd, name = tempfile.mkstemp(".html", text=True)
    with io.open(fd, "w", encoding="utf-8") as f:
        f.write(body)

    def dispose():
        try:
            os.unlink(name)
        except:
            pass

    atexit.register(dispose)
    return "file:///%s" % (
        urllib_parse.quote(name.replace("\\", "/").lstrip("/"), safe="/:"),
    )
