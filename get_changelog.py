#!/bin/env python3
# -*- coding=UTF-8 -*-
"""Get changelog for specific version.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import codecs
import os
import re

__dirname__ = os.path.abspath(os.path.dirname(__file__))
CHANGELOG_FILENAME = os.path.join(__dirname__, 'changelog.md')


def get_changelog(reader, version):
    """Get changelog from file for the version.  """

    is_started = False
    while True:
        line = reader.readline()
        if not line:
            return
        elif is_started:
            if re.match('^## ', line):
                return
            yield line
        elif re.match('^## {}( .+)?$'.format(version), line):
            is_started = True
            yield line


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    parser.add_argument('destination', nargs='?', default='-')

    args = parser.parse_args()

    outfile = (sys.stdout
    if args.destination == '-'
    else codecs.open(args.destination, 'w',encoding='utf-8'))

    with codecs.open(CHANGELOG_FILENAME, encoding='utf-8') as f:
        with outfile as dst:
            dst.writelines(get_changelog(f, args.version))

import sys
if __name__ == '__main__':
    main()
