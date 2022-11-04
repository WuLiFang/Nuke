# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import traceback

import nuke
import wulifang.vendor.cast_unknown as cast
from wulifang.nuke.infrastructure.wlf_write_node import wlf_write_node
from wulifang.vendor.pyblish import api

from .._copy_file import copy_file
from .._context_manifest import context_manifest
from ._context_task import context_task

IMAGE_KEY = "image@3f8a88bd-bb4e-478d-9147-00bcf90fda81"


class UploadImage(api.InstancePlugin):
    """上传单帧至CGTeamWork."""

    order = api.IntegratorOrder
    label = "上传单帧"
    families = ["CGTeamwork 任务"]

    def process(self, instance):
        # type: (api.Instance) -> None
        obj = instance
        ctx = obj.context
        try:
            entry = context_task(ctx)
            m = context_manifest(ctx)
            n = wlf_write_node()
            path = cast.text(nuke.filename(cast.not_none(n.node(b"Write_JPG_1"))))
            dest = cast.text(entry.filebox.get("review").path + "/{}.jpg".format(m.shot.name))  # type: ignore
            copy_file(path, dest)
            instance.data[IMAGE_KEY] = entry.set_image(dest)  # type: ignore
        except:
            traceback.print_exc()
            raise
