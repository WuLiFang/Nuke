# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


from wulifang.vendor.pyblish import api
import os

# spell-checker: word COMPUTERNAME

_KEY = "user@db1eccfa-56ff-435b-a0fd-58bba306d7cf"
_DEFAULT_USER = "%s@%s" % (
    os.getenv("USERNAME") or "anonymous",
    os.getenv("COMPUTERNAME") or "localhost",
)


def context_user(obj):
    # type: (api.Context) -> Text
    try:
        return obj.data[_KEY]
    except KeyError:
        if obj.parent:
            return context_user(obj.parent)
        return _DEFAULT_USER


def with_user(obj, manifest):
    # type: (api.Context, Text) -> None
    obj.data[_KEY] = manifest
