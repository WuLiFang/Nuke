# -*- coding=UTF-8 -*-
"""Application sentry setup.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import os

import nuke

import __version__


def setup():
    if os.getenv("SENTRY_DSN"):
        import sentry_sdk

        _ = sentry_sdk.init(
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
