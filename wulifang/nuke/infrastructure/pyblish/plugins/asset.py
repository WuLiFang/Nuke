# -*- coding=UTF-8 -*-
"""CGTeamWork pyblish plug-in.  """

from __future__ import absolute_import, division, print_function, unicode_literals

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text

import shutil
import sys
import time

from wulifang._util import cast_str, cast_text, cast_int
import nuke
from wulifang.vendor.pathlib2_unicode import PurePath
from wulifang.vendor.pyblish import api


class FootageInfo:
    def __init__(self, filename, mtime):
        # type: (Text, float) -> None

        self.filename = filename
        self.mtime = mtime


class CollectFile(api.ContextPlugin):
    """获取当前Nuke使用的文件."""

    order = api.CollectorOrder
    label = "获取当前文件"

    def process(self, context):
        context.data["comment"] = ""
        assert isinstance(context, api.Context)
        filename = nuke.value(cast_str("root.name"))
        if not filename:
            raise ValueError("工程尚未保存.")

        context.create_instance(cast_text(filename), family="工作文件")


class CollectMTime(api.ContextPlugin):
    """获取当前工程使用的素材."""

    order = api.CollectorOrder
    label = "获取素材"

    def process(self, context):
        assert isinstance(context, api.Context)
        footages = set()
        root = nuke.Root()
        for n in nuke.allNodes(cast_str("Read"), nuke.Root()):
            if n.hasError():
                self.log.warning("读取节点出错: %s", n.name())
                continue
            filename = nuke.filename(n)
            mtime = n.metadata(cast_str("input/mtime"))
            if not filename or not mtime:
                continue

            footage = FootageInfo(
                filename=cast_text(filename),
                mtime=time.mktime(
                    time.strptime(
                        cast_text(mtime),
                        "%Y-%m-%d %H:%M:%S",
                    )
                ),
            )
            footages.add(footage)
        instance = context.create_instance(
            "{}个 素材".format(len(footages)),
            filename=root[cast_str("name")].value(),
            family="素材",
        )
        instance.extend(footages)


class CollectMemoryUsage(api.ContextPlugin):
    """获取当前工程内存占用."""

    order = api.CollectorOrder
    label = "获取内存占用"

    def process(self, context):
        assert isinstance(context, api.Context)
        number = cast_int(nuke.memory(cast_str("usage")))

        context.create_instance(
            "内存占用: {}GB".format(round(number / 2.0**30, 2)),
            number=number,
            family="内存",
        )


def _is_local_file(path):
    path = cast_text(path)
    if sys.platform == "win32":
        import ctypes

        return ctypes.windll.kernel32.GetDriveTypeW(PurePath(path).drive) == 3
    return False


class ValidateFootageStore(api.InstancePlugin):
    """检查素材文件是否保存于服务器."""

    order = api.ValidatorOrder
    label = "检查素材保存位置"
    families = ["素材"]

    def process(self, instance):
        for i in instance: # type: ignore
            assert isinstance(i, FootageInfo)
            if _is_local_file(i.filename):
                raise ValueError("使用了本地素材: %s" % i.filename)


class SendToRenderDir(api.InstancePlugin):
    """发送工作文件至渲染文件夹."""

    order = api.IntegratorOrder
    label = "发送至渲染文件夹"
    families = ["工作文件"]

    def process(self, instance):
        filename = instance.data["name"]
        if nuke.numvalue(cast_str("preferences.wlf_send_to_dir"), 0.0):
            render_dir = cast_text(nuke.value(cast_str("preferences.wlf_render_dir")))
            _ = shutil.copy(filename, render_dir + "/")
        else:
            self.log.info("因为首选项设置而跳过")
