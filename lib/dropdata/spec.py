# -*- coding=UTF-8 -*-
"""Dropdata hook spec.  """

from __future__ import absolute_import, division, print_function, unicode_literals

from .core import HOOKSPEC

# pylint:disable=unused-argument


@HOOKSPEC(firstresult=True)
def is_ignore_data(data):
    """Check if data should be ignore.

    Args:
        data(unicode): dropdata.

    Returns:
        bool: check result.
    """


@HOOKSPEC
def get_url(data):
    """Get url from dropdata.

    Args:
        data(unicode): dropdata.

    Returns:
        list(unicode): File url list.
    """


@HOOKSPEC
def get_filenames(url):
    """Get filename list from url.

    Returns:
        list: filename list.
    """


@HOOKSPEC(firstresult=True)
def is_ignore_filename(filename):
    """Check if filename should be ignore.

    Args:
        filename(unicode): filename.

    Returns:
        bool: check result.
    """


@HOOKSPEC
def create_node(filename, context):
    """Create node for filename.
    Args:
        filename(unicode): filename
        context(dict): Dictionary shared between plugins.
            is_created(bool): If already created nodes.
    Returns:
        list[nuke.Node]: Created nodes.
    """


@HOOKSPEC
def after_created(nodes):
    """Modify created nodes.

    Args:
        nodes (list[nuke.Node]): Created nodes.
    """
