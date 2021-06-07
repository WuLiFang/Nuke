# -*- coding=UTF-8 -*-
"""Tools for file operations.   """
from __future__ import absolute_import, division, print_function, unicode_literals

import typing

import six

module_path: typing.Callable[..., six.text_type]
plugin_folder_path: typing.Callable[..., six.text_type]

def expand_frame(filename: six.text_type, frame: int) -> six.text_type: ...
def is_sequence_name(name: six.text_type) -> bool: ...
def get_layer(
    filename: six.text_type, layers: typing.List[six.text_type] = None
) -> typing.Optional[six.text_type]: ...
def get_tag(
    filename: six.text_type, tag_pattern: six.text_type = None
) -> six.text_type: ...
def get_shot(filename: six.text_type) -> six.text_type: ...
