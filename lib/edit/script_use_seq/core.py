# -*- coding=UTF-8 -*-
"""Switch nuke script to use sequence.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import re

import cast_unknown as cast
import nuke
from pathlib2_unicode import Path

from edit import replace_node
from edit.script_use_seq import files
from edit.script_use_seq.config import Config
from wlf.progress import progress

LOGGER = logging.getLogger(__name__)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Iterable


def get_seq(file_path):
    return re.sub(
        r'\.([\d#]+)\.',
        lambda matchobj: r'.%0{}d.'.format(len(matchobj.group(1))),
        str(file_path))


def get_seq_frames(seq_path):
    frames = set()
    p = Path(seq_path)
    for i in Path(p.parent).glob(re.sub(r'\.([\d#]+|%0?\d?d)\.', '.*.', p.name)):
        match = re.match(r'.+\.(\d+)\..+', str(i))
        if not match:
            continue
        frames.add(int(match.group(1)))
    return sorted(frames)


def _non_seq_nodes():

    for n in nuke.allNodes(b"Read", nuke.Root()):
        filename = nuke.filename(n)
        if filename == get_seq(filename) and not n.hasError():
            continue
        yield n


def replace_footages(cfg, footages=None):
    if footages is None:
        for _ in progress(['获取文件列表……'], '匹配素材文件'):
            footages = files.search(
                include=cfg['seq_include'].splitlines(),
                exclude=cfg['seq_exclude'].splitlines())
    name_footage_map = {i.name: i for i in (Path(j) for j in footages)}
    LOGGER.info("Got footages: count=%d", len(name_footage_map))
    for n in _non_seq_nodes():
        name = Path(cast.text(nuke.filename(n))).name
        if name not in name_footage_map:
            LOGGER.warning("No footage match: filename=%s", name)
            continue
        footage = name_footage_map[name]
        seq = get_seq(footage)
        cast.instance(
            n[b'file'],
            nuke.File_Knob,
        ).fromUserText(
            cast.binary(seq))
        frames = get_seq_frames(seq)
        if frames:
            first = min(frames)
            last = max(frames)
            _ = n[b'first'].setValue(first)
            _ = n[b'origfirst'].setValue(first)
            _ = n[b'last'].setValue(last)
            _ = n[b'origlast'].setValue(last)


def _replace_write_node(cfg):
    if not cfg['use_wlf_write']:
        return
    if len(nuke.allNodes(b"wlf_Write")) > 0:
        return
    nodes = nuke.allNodes(b'Write', nuke.Root())
    if not nodes:
        return
    assert len(nodes) == 1, "Too many write node: count=%d" % len(nodes)
    write_node = nodes[0]

    n = nuke.nodes.wlf_Write(
        inputs=[write_node.input(0)],
        xpos=write_node.xpos(),
        ypos=write_node.ypos(),
    )
    replace_node(write_node, n)
    nuke.delete(write_node)


def replace_nodes(cfg):
    _replace_write_node(cfg)


def _config_frame_range(cfg):
    if not cfg['is_auto_frame_range']:
        return
    nodes = [i for i in nuke.allNodes(b'Read')
             if i.firstFrame() != i.lastFrame() and not i.hasError()]
    if not nodes:
        return
    first = max(i.firstFrame() for i in nodes)
    last = max(i.lastFrame() for i in nodes)
    root = nuke.Root()
    _ = root[b'first_frame'].setValue(first)
    _ = root[b'last_frame'].setValue(last)


def _config_project_directory(cfg):
    new_value = cfg['override_project_directory']
    if not new_value:
        return
    _ = nuke.Root()[b'project_directory'].setValue(new_value)


def config_project(cfg):
    _config_frame_range(cfg)
    _config_project_directory(cfg)


def execute(footages=None):
    # type: (Iterable[Text]) -> None
    cfg = Config()
    replace_footages(cfg, footages=footages)
    replace_nodes(cfg)
    config_project(cfg)
