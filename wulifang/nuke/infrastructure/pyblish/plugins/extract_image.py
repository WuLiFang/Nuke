# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import wulifang.vendor.cast_unknown as cast
import nuke
from wulifang.nuke.infrastructure.recover_modifield_flag import recover_modifield_flag
from wulifang.nuke.infrastructure.wlf_write_node import wlf_write_node
from wulifang.vendor.pyblish import api
import wulifang


class ExtractImage(api.InstancePlugin):
    """生成单帧图."""

    order = api.ExtractorOrder
    label = "生成单帧图"
    families = ["工作文件"]

    def process(self, instance):
        # type: (api.Instance) -> None
        with recover_modifield_flag():
            if not nuke.numvalue(b"preferences.wlf_render_jpg", 0.0):
                self.log.info("因首选项而跳过生成JPG")
                return

            n = wlf_write_node()
            if n:
                self.log.debug("render_jpg: %s", n.name())
                try:
                    cast.instance(n[b"bt_render_JPG"], nuke.Script_Knob).execute()
                except RuntimeError as ex:
                    wulifang.message.error("生成JPG: %s" % ex)
            else:
                self.log.warning("工程中缺少wlf_Write节点")
