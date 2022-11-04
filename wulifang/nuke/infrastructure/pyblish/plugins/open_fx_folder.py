# -*- coding=UTF-8 -*-
"""CGTeamWork pyblish plug-in.  """

from __future__ import absolute_import, division, print_function, unicode_literals
import traceback


import os
import webbrowser

from wulifang.vendor.pyblish import api
import os


class OpenFXFolder(api.InstancePlugin):
    """打开特效素材的文件夹."""

    order = api.ValidatorOrder
    label = "打开素材文件夹"
    families = ["特效素材"]

    def process(self, instance):
        p = instance.data["folder"]
        if not os.path.exists(p):
            return
        try:
            webbrowser.open(p)
        except:
            traceback.print_exc()
