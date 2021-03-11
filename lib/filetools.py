# -*- coding=UTF-8 -*-
"""Tools for file operations.   """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
import typing

import wlf.path
from wlf.codectools import get_unicode
from wlf.pathtools import make_path_finder

module_path = make_path_finder(__file__)  # pylint: disable = invalid-name
plugin_folder_path = make_path_finder(  # pylint: disable = invalid-name
    module_path())


if typing.TYPE_CHECKING:
    import six
    _ = six


def expand_frame(filename, frame):
    # type: (str, int) -> str
    """expand frame number placeholder in filename, support # and %0d style.

    Args:
        filename (six.text_type): filename
        frame (int): frame number

    >>> six.text_type(expand_frame('test_sequence_###.exr', 1))
    u'test_sequence_001.exr'
    >>> six.text_type(expand_frame('test_sequence_369.exr', 1))
    u'test_sequence_369.exr'
    >>> six.text_type(expand_frame('test_sequence_%03d.exr', 1234))
    u'test_sequence_1234.exr'
    >>> six.text_type(expand_frame('test_sequence_%03d.###.exr', 1234))
    u'test_sequence_1234.1234.exr'
    """

    def _format_repl(matchobj):
        return matchobj.group(0) % frame

    def _hash_repl(matchobj):
        return '%0{}d'.format(len(matchobj.group(0)))

    ret = get_unicode(filename)
    ret = re.sub(r'(\#+)', _hash_repl, ret)
    ret = re.sub(r'(%0?\d*d)', _format_repl, ret)
    return ret


def is_sequence_name(name):
    # type: (str) -> bool
    """check if {name} is a sequence.

    Args:
        name (str): filename

    Returns:
        [bool]: filename is a sequence
    """
    return expand_frame(name, 1) != expand_frame(name, 2)


def get_layer(filename, layers=None):
    # type: (str, typing.Optional[typing.List[str]]) -> str
    """The footage layer name.

    >>> get_layer('Z:/MT/Render/image/MT_BG_co/MT_BG_co_PuzzleMatte1/PuzzleMatte1.001.exr')
    u'PuzzleMatte1'
    """

    path = wlf.path.PurePath(filename)
    if layers is not None:
        path.layers = layers
    return path.layer


def get_tag(filename, tag_pattern=None):
    # type: (str, typing.Optional[str]) -> str
    """The footage tag name.

    >>> get_tag('Z:/MT/Render/image/MT_BG_co/MT_BG_co_PuzzleMatte1/PuzzleMatte1.001.exr')
    u'PuzzleMatte1'
    """

    path = wlf.path.PurePath(filename)
    if tag_pattern is not None:
        path.tag_pattern = tag_pattern
    return path.tag

def get_shot(filename):
    # type: (str) -> str
    """The related shot for this footage.

    >>> get_shot('sc_001_v20.nk')
    u'sc_001'
    >>> get_shot('hello world')
    u'hello world'
    >>> get_shot('sc_001_v-1.nk')
    u'sc_001_v-1'
    >>> get_shot('sc001V1.jpg')
    u'sc001'
    >>> get_shot('sc001V1_no_bg.jpg')
    u'sc001'
    >>> get_shot('suv2005_v2_m.jpg')
    u'suv2005'
    """

    return wlf.path.PurePath(filename).shot
