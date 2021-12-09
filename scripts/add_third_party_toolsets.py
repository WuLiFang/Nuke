#!/usr/bin/python3
# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
from typing import Text
import sys
import os
import argparse

_LOGGER = logging.getLogger(__name__)
__dirname__ = os.path.dirname(__file__)
_WORKSPACE_FOLDER = os.path.abspath(
    os.path.join(__file__, "../../ToolSets/third_party/")
)

import re


def _gizmo_to_nk(content: Text, name: Text) -> Text:
    ret, count = re.subn(r"^Gizmo {$", "Group {\n name %s1" % name, content, flags=re.M)
    if count != 1:
        _LOGGER.warn(
            "should has exact one gizmo node: name='%s' actual=%d" % (name, count)
        )
    return ret


def _add_file(filename: Text):
    _LOGGER.debug("add_file: %s", filename)

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    name, ext = os.path.splitext(os.path.basename(filename))
    if ext == ".gizmo":
        content = _gizmo_to_nk(content, name)

    dst = os.path.join(_WORKSPACE_FOLDER, name + ".nk")
    with open(dst, "w", encoding="utf-8") as f:
        _ = f.write(content)
    _LOGGER.info(
        "added: %s",
        os.path.relpath(
            dst,
            _WORKSPACE_FOLDER,
        ),
    )


def _cli_add_file(filename: Text):
    if filename == "-":
        for i in sys.stdin.readlines():
            p = i.strip("\r\n")
            if not p:
                continue
            _add_file(p)
        return
    _add_file(filename)


def main():
    logging.basicConfig(level="DEBUG")
    parser = argparse.ArgumentParser()
    _ = parser.add_argument("filenames", nargs="+")
    args = parser.parse_args()
    for i in args.filenames:
        _cli_add_file(i)


if __name__ == "__main__":
    main()
