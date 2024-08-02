# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

from wulifang.vendor.pyblish import api
from wulifang.vendor.cgtwq import F

TYPE_CHECKING = False
if TYPE_CHECKING:
    from wulifang.vendor.cgtwq import Client, RowID


_KEY = "task@23b4df7c-8ef8-41a4-8cc0-b387583011d3"


class Task:
    def __init__(self, client, id):
        # type: (Client, RowID) -> None
        self.client = client
        self.id = id

    def table(self):
        return self.client.table(
            self.id.database,
            self.id.module,
            self.id.module_type,
            filter_by=F("#id").equal(self.id.value),
        )


def context_task(ctx):
    # type: (api.Context) -> Task
    try:
        return ctx.data[_KEY]
    except KeyError:
        if ctx.parent:  # type: ignore
            return context_task(ctx.parent)  # type: ignore
        raise ValueError("无 CGTeamwork 任务")


def with_task(ctx, task):
    # type: (api.Context, Task) -> None
    ctx.data[_KEY] = task
