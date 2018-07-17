# -*- coding=UTF-8 -*-
"""Test module `asset.autofix`.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import nuke

from asset import autofix
from nodeutil import is_node_deleted


def _dummy_filename_dict():
    assert nuke.frame() == 0
    return {
        'a.exr': '/test/a.exr',
        'a.0000.exr': '/test/a.####.exr',
    }


def test_fix_read(monkeypatch):
    monkeypatch.setattr(autofix, '_filename_dict', _dummy_filename_dict)
    monkeypatch.setattr(autofix, 'IS_TESTING', True)
    for node_class in ('Read',
                       'DeepRead',
                       'ReadGeo2'):
        print(node_class)
        addtional_knobs = {}
        node_class = getattr(nuke.nodes, node_class)

        n = node_class(file='/404/a.exr', **addtional_knobs)
        assert n.hasError()
        autofix.fix_read()
        assert n['file'].value() == '/test/a.exr'
        n = node_class(file='/404/a.%04d.exr', **addtional_knobs)
        assert n.hasError()
        autofix.fix_read()
        assert n['file'].value() == '/test/a.%04d.exr'
        n = node_class(file='/404/thumbs.db', **addtional_knobs)
        autofix.fix_read()
        assert is_node_deleted(n)
