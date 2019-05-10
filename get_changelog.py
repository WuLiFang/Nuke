# -*- coding=UTF-8 -*-
"""Get changelog for sepecific version.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import codecs
import os
import re
import sys
from collections import namedtuple

__dirname__ = os.path.abspath(os.path.dirname(__file__))
CHANGELOG_DIR = os.path.join(__dirname__, 'changelogs')


def _changelogs():
    return


def get_file(version):
    """Get changelog file for the version.  """

    assert isinstance(version, Version), type(version)
    files = os.listdir(CHANGELOG_DIR)
    pattern = re.compile(
        r'\d+_{0.major}\.{0.minor}\.md'.format(version), flags=re.I)
    try:
        return next(os.path.join(CHANGELOG_DIR, i)
                    for i in files if pattern.match(i))
    except StopIteration:
        raise ValueError('Can not found changelog file.')


def get_changelog(filename, version):
    """Get changelog from file for the version.  """

    assert isinstance(version, Version), type(version)
    groups = []
    with codecs.open(filename, encoding='utf-8') as f:
        is_start = False
        while True:
            line = f.readline()
            if not line:
                break
            elif re.match('^#+', line):
                is_start = True
                group = []
                groups.append(group)
            if is_start:
                group.append(line)
    return [group for group in groups
            if re.match(
                r'^#+ {0.major}\.{0.minor}(?:\.{0.patch})?$'.format(version),
                group[0].replace('\r\n', '\n'))][-1]


class Version(namedtuple('Version', ('major', 'minor', 'patch'))):
    """Semantic version."""
    @classmethod
    def parse(cls, text):
        """Get version from text.  """

        parts = re.split(r'\.|-', text)[:3]
        if len(parts) == 2:
            parts.append('0')
        return cls(*parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    parser.add_argument('destination')

    args = parser.parse_args()

    version = Version.parse(args.version)

    filename = get_file(version)
    result = get_changelog(filename, version)
    with codecs.open(args.destination, 'w', 'utf-8') as f:
        f.writelines(result)


if __name__ == '__main__':
    main()
