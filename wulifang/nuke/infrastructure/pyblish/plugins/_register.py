# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

from wulifang.vendor.pyblish import api

from .asset import (
    CollectFile,
    CollectMemoryUsage,
    CollectMTime,
)
from .collect_manifest import CollectManifest
from .extract_image import ExtractImage
from .open_fx_folder import OpenFXFolder
from .save_manifest import SaveManifest
from .validate_fps import ValidateFPS
from .validate_frame_range import ValidateFrameRange
from .validate_nuke_version import ValidateNukeVersion
from .validate_resolution import ValidateResolution


def register():
    for i in (
        CollectFile,
        CollectMemoryUsage,
        CollectMTime,
        CollectManifest,
        ExtractImage,
        ValidateFrameRange,
        ValidateResolution,
        ValidateFPS,
        OpenFXFolder,
        SaveManifest,
        ValidateNukeVersion,
    ):
        api.register_plugin(i)
