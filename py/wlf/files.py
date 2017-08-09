# -*- coding=UTF-8 -*-
"""Non-nuke-invoked files operation. """

import os
import re
import shutil
import locale
import string
import warnings
from subprocess import call, Popen

from wlf.config import Config

try:
    import nuke
    HAS_NUKE = True
except ImportError:
    HAS_NUKE = False

__version__ = '0.4.1'


REDSHIFT_LAYERS = ('DiffuseLighting', 'SSS', 'Reflections',
                   'Refractions', 'GI', 'Emission', 'Caustics',
                   'SpecularLighting', 'Z', 'P', 'BumpNormals',
                   'DiffuseFilter', 'MotionVectors', 'TransTint',
                   'PuzzleMatte')


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
        call(get_encoded(u'XCOPY /V /Y "{}" "{}"'.format(src, dst)))
    if os.path.isdir(get_encoded(dst)):
        ret = os.path.join(dst, os.path.basename(src))
    else:
        ret = dst
    return ret


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
    >>> split_version('sc001V1.jpg')
    ('sc001', 1)
    >>> split_version('sc001V1_no_bg.jpg')
    ('sc001', 1)
    >>> split_version('suv2005_v2_m.jpg')
    ('suv2005', 2)
    """

    match = re.match(r'(.+)v(\d+)', f, flags=re.I)
    if not match:
        return (os.path.splitext(f)[0], None)
    shot, version = match.groups()
    return (shot.strip('_'), int(version))


def remove_version(path):
    """Return filename without version number.

    >>> remove_version('sc_001_v233.jpg')
    'sc_001.jpg'
    """
    shot = split_version(path)[0]
    ext = os.path.splitext(path)[1]
    return '{}{}'.format(shot, ext)


def map_drivers():
    """Map unc path. """
    cmd = r'(IF NOT EXIST X: NET USE X: \\192.168.1.4\h) &'\
        r'(IF NOT EXIST Y: NET USE Y: \\192.168.1.7\y) &'\
        r'(IF NOT EXIST Z: NET USE Z: \\192.168.1.7\z)'
    call(cmd, shell=True)


def url_open(url, isfile=False):
    """Open url in explorer. """
    if isfile:
        url = 'file://{}'.format(url)
    _cmd = u"rundll32.exe url.dll,FileProtocolHandler {}".format(url)
    Popen(get_encoded(_cmd))


def unicode_popen(args, **kwargs):
    """Return Popen object use encoded args.  """
    with warnings.catch_warnings():
        warnings.simplefilter('always')
        warnings.warn(
            'Use Popen(get_encoded(arg) Instead.', DeprecationWarning)
    if isinstance(args, unicode):
        args = get_encoded(args)
    return Popen(args, **kwargs)


def get_unicode(input_str, codecs=('UTF-8', 'GBK')):
    """Return unicode by try decode @string with @codecs.  """

    if isinstance(input_str, unicode):
        return input_str

    for i in tuple(codecs) + tuple(locale.getdefaultlocale()[1]):
        try:
            return unicode(input_str, i)
        except UnicodeDecodeError:
            continue


def get_encoded(input_str, encoding=None):
    """Return unicode by try decode @string with @encodeing.  """
    if encoding is None:
        encoding = locale.getdefaultlocale()[1]

    return get_unicode(input_str).encode(encoding)


def is_ascii(text):
    """Return true if @text can be convert to ascii.

    >>> is_ascii('a')
    True
    >>> is_ascii('测试')
    False

    """
    try:
        get_unicode(text).encode('ASCII')
        return True
    except UnicodeEncodeError:
        return False


def get_layer(filename):
    """Return layer name from @filename.

    >>> get_layer('Z:/MT/Render/image/MT_BG_co/MT_BG_co_PuzzleMatte1/PuzzleMatte1.001.exr')
    'PuzzleMatte1'
    """

    basename = os.path.basename(filename)
    for layer in REDSHIFT_LAYERS:
        match = re.search(r'\b({}\d*)\b'.format(layer), basename)
        if match:
            return match.group(1)


def checked_exists(checking_list):
    """Return file existed item in @checking_list.  """
    if HAS_NUKE:
        task = nuke.ProgressTask('验证文件')
        checking_list = list(checking_list)
        all_num = len(checking_list)

    def _check(index, i):
        if HAS_NUKE:
            task.setProgress(index * 100 // all_num)
            task.setMessage(i)
        return os.path.exists(get_encoded(i))
    return (i for index, i in enumerate(checking_list) if _check(index, i))


def get_tag(filename, pat=None, default=Config.default_tag):
    """Return tag of @filename from @pat.

    >>> get_tag('Z:/MT/Render/image/MT_BG_co/MT_BG_co_Z/Z.001.exr', r'MT_(.+)_')
    u'BG'
    >>> get_tag('MT_BG_co_Z', r'MT_(.+)_')
    u'BG'
    >>> get_tag('Z.001.exr', r'MT_(.+)_')
    u'Z'
    >>> # cases below will use default pattern.
    >>> default_pat = Config.default['tag_pat']
    >>> get_tag(r'Z:\\QQFC2017\\Render\\SC_065\\QQFC_sc065_CH2', default_pat)
    u'CH2'
    >>> get_tag(r'Z:\\EP13_09_sc151_CH_B\\EP13_09_sc151_CH_B.0015.exr', default_pat)
    u'CH_B'
    >>> # result of below case has been auto converted by a dictionary(BG_CO -> BG).
    >>> get_tag('Z:/MT/Render/image/MT_BG_co/MT_BG_co_Z/Z.001.exr', default_pat)
    u'BG'
    >>> get_tag('Z:/QQFC2017/Render/SC_031a/sc_031a_CH_B_ID/sc_031a_CH_B_ID.####.exr', default_pat)
    u'CH_B'
    """

    pat = pat or Config().get('tag_pat')
    ret = None
    for testing_pat in set((pat, Config.default['tag_pat'])):
        tag_pat = re.compile(testing_pat, flags=re.I)
        for test_string in\
                (os.path.basename(os.path.dirname(filename)), os.path.basename(filename)):
            ret = re.match(tag_pat, test_string)
            if ret and ret.group(1):
                ret = ret.group(1).strip('_').upper()
                break
            else:
                ret = None
        if ret:
            break
    else:
        ret = default

    ret = Config.tag_convert_dict.get(ret, ret)

    if ret.startswith(tuple(string.digits)):
        ret = '_{}'.format(ret)
    return get_unicode(ret)


def escape_batch(text):
    """Return escaped text for windows shell.

    >>> escape_batch('test_text "^%~1"')
    u'test_text \\\\"^^%~1\\\\"'
    >>> escape_batch(u'中文 \"^%1\"')
    u'\\xe4\\xb8\\xad\\xe6\\x96\\x87 \\\\"^^%1\\\\"'
    """

    return text.replace(u'\\', u'\\\\').replace(u'^', r'^^').replace(u'"', r'\"')


def traytip(title, text, seconds=3, options=1):
    """Show a traytip(windows only).  """

    executable = os.path.abspath(
        os.path.join(__file__, '../../../traytip.exe'))
    if not os.path.exists(get_encoded(executable)):
        raise IOError('traytip.exe missing')
    cmd = '"{}" "{}" "{}" "{}" "{}"'.format(
        executable, escape_batch(title), escape_batch(text), seconds, options)
    Popen(get_encoded(cmd))
