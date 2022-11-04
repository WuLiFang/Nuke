# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

from wulifang.vendor.pyblish import api

from .collect_animation_video import CollectAnimationVideo
from .collect_fx_footage import CollectFXFootage
from .collect_task import CollectTask
from .collect_user import CollectUser
from .submit import Submit
from .upload_image import UploadImage
from .upload_precomp import UploadPrecomp
from .upload_script import UploadScript
from .upload_manifest import UploadManifest
from .validate_artist import ValidateArtist
from .validate_leader_status import ValidateLeaderStatus


def register():
    for i in (
        CollectAnimationVideo,
        CollectFXFootage,
        CollectTask,
        CollectUser,
        Submit,
        UploadImage,
        UploadPrecomp,
        UploadScript,
        UploadManifest,
        ValidateArtist,
        ValidateLeaderStatus,
    ):
        api.register_plugin(i)
