# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals

import base64

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text


def create_iife(_python_script):
    # type: (Text) -> Text
    return (
        r"""eval(compile('import base64;eval(compile(base64.b64decode("%s"), "<iife-inner>", "exec"))', "<iife-outer>", "exec"), None, {})"""
        % (base64.b64encode(_python_script.encode("utf-8")).decode("utf-8"),)
    )
