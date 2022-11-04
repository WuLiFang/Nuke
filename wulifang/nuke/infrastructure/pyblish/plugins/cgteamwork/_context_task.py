# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


from wulifang.vendor.pyblish import api
import wulifang.vendor.cgtwq as cgtwq

_KEY = "task@23b4df7c-8ef8-41a4-8cc0-b387583011d3"


def context_task(ctx):
    # type: (api.Context) -> cgtwq.Entry
    try:
        return ctx.data[_KEY]
    except KeyError:
        if ctx.parent:
            return context_task(ctx.parent)
        raise ValueError("无 CGTeamwork 任务")


def with_task(ctx, task):
    # type: (api.Context, cgtwq.Entry) -> None
    ctx.data[_KEY] = task
