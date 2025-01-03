# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import traceback
from string import Template

import nuke

from wulifang.vendor.pyblish import api

from wulifang.nuke._util import (
    wlf_write_node,
)
from wulifang._util import (
    cast_str,
    cast_text,
    assert_not_none,
)
from .._context_manifest import context_manifest
from ._context_task import context_task

IMAGE_KEY = "image@3f8a88bd-bb4e-478d-9147-00bcf90fda81"

_EXTENSION_KEY = "548842a5-c893-4104-88ce-7184c8bb3c8c"


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
            task = context_task(ctx)
            m = context_manifest(ctx)
            n = wlf_write_node()
            src = cast_text(
                nuke.filename(assert_not_none(n.node(cast_str("Write_JPG_1"))))
            )
            nameTemplate = "${shot_name}"
            if _EXTENSION_KEY in m.extension:
                opts = m.extension[_EXTENSION_KEY]
                nameTemplate = opts.get("imageName", nameTemplate)
            image_name, ext = os.path.splitext(os.path.basename(src))
            script_name, _ = os.path.splitext(
                os.path.basename(cast_text(nuke.scriptName()))
            )
            script_dir, _ = os.path.splitext(
                os.path.basename(cast_text(nuke.script_directory()))
            )
            name = cast_text(
                Template(nameTemplate).substitute(
                    dict(
                        shot_name=m.shot.name,
                        image_name=image_name,
                        script_name=script_name,
                        script_dir=script_dir,
                        project_name=m.project.name,
                        segment_name=m.project.segment.name,
                    )
                )
            )
            dest_name = name + ext
            self.log.info("单帧图上传为: %s" % (dest_name,))
            image = task.client.image.upload(task.id.database, src)
            dest_dir = next(task.client.file_box.all_submit(task.id)).path  # type: ignore
            dest = os.path.join(dest_dir, dest_name)
            task.client.set((task.id,), {"image": image})
            instance.data[IMAGE_KEY] = (image, dest)  # type: ignore
        except:
            traceback.print_exc()
            raise
