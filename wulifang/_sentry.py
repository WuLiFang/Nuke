# -*- coding=UTF-8 -*-
"""Application sentry setup.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import os

import nuke

from wulifang import __version__

from wulifang._util import PY2


def init():
    # FIXME: not work in python2
    if not PY2 and os.getenv("SENTRY_DSN"):
        from wulifang.vendor import sentry_sdk

        sentry_sdk.init(  # type: ignore
            os.getenv("SENTRY_DSN"),
            release=__version__.VERSION,
            debug=os.getenv("DEBUG") == "sentry",
        )
        sentry_sdk.set_context(
            "Nuke",
            dict(
                version=nuke.NUKE_VERSION_STRING,
                gui=nuke.GUI,
            ),
        )
