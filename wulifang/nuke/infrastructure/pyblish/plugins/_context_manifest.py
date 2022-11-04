# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import wulifang.vendor.wulifang_manifest as m6t
from wulifang.vendor.pyblish import api

_KEY = "manifest@31fc76e0-028b-40fa-9f5f-3e693b608247"


def context_manifest(obj):
    # type: (api.Instance) -> m6t.Manifest
    try:
        return obj.data[_KEY]
    except KeyError:
        if obj.parent:
            return context_manifest(obj.parent)
        raise ValueError("无清单文件")


def with_manifest(obj, manifest):
    # type: (api.Instance, m6t.Manifest) -> None
    obj.data[_KEY] = manifest
