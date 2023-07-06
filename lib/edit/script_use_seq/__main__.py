# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false
"""Switch nuke script to use sequence.  """

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import io
import os
import sys

import nuke

import wulifang.vendor.cast_unknown as cast
from wulifang.vendor.pathlib2_unicode import Path


def main():
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    import edit.script_use_seq as _script_use_seq

    _ = sys.stdout.write(cast.text(_script_use_seq.config.START_MESSAGE))
    parser = argparse.ArgumentParser(description="Switch nuke script to use sequence.")
    _ = parser.add_argument("--input", help=".nk input file path")
    _ = parser.add_argument("--output", help=".nk output file path.")
    _ = parser.add_argument(
        "--footage-list", nargs="?", help="potential footage list file"
    )
    args = parser.parse_args(sys.argv[1:])
    output = cast.text(args.output)

    footages = None
    if args.footage_list:
        with io.open(args.footage_list, encoding="utf8") as f:
            footages = f.read().splitlines()
            assert footages
    nuke.scriptOpen(cast.binary(args.input))
    _script_use_seq.execute(footages=footages)
    nuke.Root()[b"name"].setValue(args.output)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    _ = nuke.scriptSave(cast.binary(args.output))


if __name__ == "__main__":
    main()
