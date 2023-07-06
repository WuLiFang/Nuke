# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text

from wulifang._util import cast_text
from wulifang.vendor.pyblish import api

from ._context_task import context_task

_KEY = "workFileDir@e867ccf0-5cbf-4419-b03d-6198f8236850"


def context_work_file_dir(ctx):
    # type: (api.Context) -> Text
    if _KEY not in ctx.data:
        entry = context_task(ctx)
        try:
            work_file_box = entry.filebox.get("workfile")
        except:
            raise ValueError("找不到标识为 workfile 的文件框 请联系管理员进行设置")
        v = cast_text(work_file_box.path) + "/"  # type: ignore
        ctx.data[_KEY] = v
    return ctx.data[_KEY]
