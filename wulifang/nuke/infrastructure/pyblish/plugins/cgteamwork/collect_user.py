# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


from wulifang.vendor.pyblish import api
from wulifang.vendor.cgtwq import desktop as cgtw, F
from .._context_user import with_user

NAME_KEY = "userName@1da2ed53-f288-40e9-add8-7d9fef12840c"
ACCOUNT_KEY = "account@1da2ed53-f288-40e9-add8-7d9fef12840c"
ACCOUNT_ID_KEY = "accountID@1da2ed53-f288-40e9-add8-7d9fef12840c"

import email.utils

email.utils.formataddr


class CollectUser(api.ContextPlugin):
    """获取当前登录的 CGTeamwork 帐号."""

    order = api.CollectorOrder
    label = "获取当前用户"

    def process(self, context):
        # type: (api.Context) -> None
        client = cgtw.current_client()
        if not client:
            return

        for login, name in client.table(
            "public",
            "account",
            "info",
            filter_by=F("account.id").equal(client.token.user_id),
        ).rows("account.entity", "account.name"):
            context.data[NAME_KEY] = name
            context.data[ACCOUNT_KEY] = login
            context.data[ACCOUNT_ID_KEY] = client.token.user_id
            user = "%s (%s)" % (login, name)
            user_addr = "%s <%s@cgteamwork>" % (name, login)
            with_user(context, user_addr)
            context.create_instance(
                "CGTeamwork 用户: %s" % (user,), family="CGTeamwork 用户"
            )
