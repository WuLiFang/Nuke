# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

from wulifang.vendor.wlf import path as wlf_path

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def shot_from_filename(_filename):
    # type: (Text) -> Text
    """The related shot for this footage.

    >>> shot_from_filename('sc_001_v20.nk')
    u'sc_001'
    >>> shot_from_filename('hello world')
    u'hello world'
    >>> shot_from_filename('sc_001_v-1.nk')
    u'sc_001_v-1'
    >>> shot_from_filename('sc001V1.jpg')
    u'sc001'
    >>> shot_from_filename('sc001V1_no_bg.jpg')
    u'sc001'
    >>> shot_from_filename('suv2005_v2_m.jpg')
    u'suv2005'
    """

    # TODO: avoid use of library
    return wlf_path.PurePath(_filename).shot # type: ignore
