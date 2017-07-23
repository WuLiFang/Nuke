# -*- coding=UTF-8 -*-
"""Non-nuke-invoked files operation. """

import os
import re
import shutil
import locale
from subprocess import call, Popen

__version__ = '0.1.1'
OS_ENCODING = locale.getdefaultlocale()[1]


def copy(src, dst):
    """Copy src to dst."""

    message = u'{} -> {}'.format(src, dst)
    print(message)
    if not os.path.exists(src):
        return
    dst_dir = os.path.dirname(dst)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    try:
        shutil.copy2(src, dst)
    except WindowsError:
        call(u'XCOPY /V /Y "{}" "{}"'.format(src, dst).encode(OS_ENCODING))


def version_filter(iterable):
    """Keep only newest version for each shot, try compare mtime when version is same.

    >>> version_filter(('sc_001_v1', 'sc_001_v2', 'sc002_v3', 'thumbs.db'))
    ['sc002_v3', 'sc_001_v2', 'thumbs.db']
    """
    shots = {}
    iterable = sorted(
        iterable, key=lambda x: split_version(x)[1], reverse=True)
    for i in iterable:
        shot, version = split_version(i)
        shot = shot.lower()
        shots.setdefault(shot, {})
        shots[shot].setdefault('path_list', [])
        if version > shots[shot].get('version'):
            shots[shot]['path_list'] = [i]
            shots[shot]['version'] = version
        elif version == shots[shot].get(version):
            shots[shot]['path_list'].append(i)

    for shot in shots:
        shots[shot] = sorted(
            shots[shot]['path_list'],
            key=lambda shot:
            os.path.getmtime(shot) if os.path.exists(shot) else None,
            reverse=True)[0]
    return sorted(shots.values())


def expand_frame(filename, frame):
    '''Return a frame mark expaned version of filename, with given frame.

    >>> expand_frame('test_sequence_###.exr', 1)
    'test_sequence_001.exr'
    >>> expand_frame('test_sequence_369.exr', 1)
    'test_sequence_369.exr'
    >>> expand_frame('test_sequence_%03d.exr', 1234)
    'test_sequence_1234.exr'
    >>> expand_frame('test_sequence_%03d.###.exr', 1234)
    'test_sequence_1234.1234.exr'
    '''
    def _format_repl(matchobj):
        return matchobj.group(0) % frame

    def _hash_repl(matchobj):
        return '%0{}d'.format(len(matchobj.group(0)))
    ret = filename
    ret = re.sub(r'(\#+)', _hash_repl, ret)
    ret = re.sub(r'(%0?\d*d)', _format_repl, ret)
    return ret


def split_version(f):
    """Return nuke style _v# (shot, version number) pair.

    >>> split_version('sc_001_v20.nk')
    ('sc_001', 20)
    >>> split_version('hello world')
    ('hello world', None)
    >>> split_version('sc_001_v-1.nk')
    ('sc_001_v-1', None)
    """

    match = re.match(r'(.+)_v(\d+)', f)
    if not match:
        return (os.path.splitext(f)[0], None)
    shot, version = match.groups()
    return (shot, int(version))


def remove_version(path):
    """Return filename without version number.

    >>> remove_version('sc_001_v233.jpg')
    'sc_001.jpg'
    """
    shot = split_version(path)[0]
    ext = os.path.splitext(path)[1]
    return '{}{}'.format(shot, ext)


def url_open(url):
    """Open url in explorer. """
    _cmd = u"rundll32.exe url.dll,FileProtocolHandler {}".format(url)
    unicode_popen(_cmd)


def unicode_popen(args, **kwargs):
    """Return Popen object use encoded args.  """

    if isinstance(args, unicode):
        args = args.encode(OS_ENCODING)
    return Popen(args, **kwargs)
