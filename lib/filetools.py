# -*- coding=UTF-8 -*-
"""Tools for file operations.   """
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
import six

from wlf.pathtools import make_path_finder
from wlf.codectools import get_unicode

module_path = make_path_finder(__file__)  # pylint: disable = invalid-name
plugin_folder_path = make_path_finder(  # pylint: disable = invalid-name
    module_path())


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
