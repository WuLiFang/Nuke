# -*- coding=UTF-8 -*-
"""Auto fix wrong nodes.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import os

import nuke

import dropdata
from wlf.codectools import get_encoded as e
from wlf.codectools import u_print
from wlf.path import PurePath

LOGGER = logging.getLogger(__name__)
IS_TESTING = False


def fix_read():
    """Try fix all nodes that has filename error."""

    result = [_fix_one(n, filename_dict=_filename_dict())
              for n in _errored_nodes()]
    result = {
        'success': result.count(True),
        'fail': result.count(False)
    }
    nuke.message('成功修复 {success} 个节点, 失败 {fail} 个'.format(
        **result).encode('utf-8'))
    return result


def _fix_one(n, **context):
    filename = _u_nuke_filename(n)
    if not filename:
        return None
    context['filename'] = filename
    context['node'] = n
    context['name'] = n.name()
    ret = (_fix_thumbs_db(context)
           or _fix_missing_file(context)
           or _fix_dir(context))
    if not context.get('alter_filename'):
        u_print('修复读取: 找不到可替换素材: {name}: {filename}'.format(**context))
    return ret


def _filename_dict():
    filenames = set(_u_nuke_filename(n)
                    for n in nuke.allNodes()
                    if not n.hasError())
    return {_current_basename(i): i for i in filenames}


def _u_nuke_filename(node):
    value = nuke.filename(node)
    if value is None:
        return None
    return value.decode('utf-8')


def _set_filename(n, value):
    try:
        k = (n['file'] if not n['proxy'].value()
             or nuke.value('root.proxy') == 'false' else n['proxy'])
    except NameError:
        k = n['file']
    k.setValue(value.encode('utf-8'))


def _errored_nodes():
    ret = set()
    for n in nuke.allNodes():
        try:
            if not n.hasError() or n['disable'].value():
                continue
            ret.add(n)
        except NameError:
            continue
    return ret


def _fix_thumbs_db(context):
    n = context['node']
    filename = context['filename']
    if filename and os.path.basename(filename).lower() == 'thumbs.db':
        nuke.delete(n)
        u_print('修复读取: 删除读取thumbs.db的节点: {name}'.format(**context))
        return True
    return False


def _fix_missing_file(context):
    n = context['node']
    filename = context['filename']
    filename_dict = context['filename_dict']
    key = _current_basename(filename)
    value = filename_dict.get(key)
    if value:
        context['alter_filename'] = value
        _set_filename(n, value)
        if not IS_TESTING and n.hasError():
            u_print('修复读取: 使用新素材依旧出错, 撤销: '
                    '{name}: {alter_filename}'.format(**context))
            _set_filename(n, filename)
            return False
        u_print('修复读取: 使用同名文件: '
                '{name}: {filename} -> {alter_filename}'.format(**context))
        return True
    return False


def _fix_dir(context):
    filename = context['filename']
    n = context['node']
    if not os.path.isdir(e(filename)):
        return False

    is_dropped = dropdata.drop('text/plain', filename)
    if is_dropped:
        u_print('修复读取: 文件夹展开: {name}: {filename}'.format(**context))
        nuke.delete(n)
    return is_dropped


def _current_basename(filename):
    if not filename:
        return None
    return PurePath(filename).with_frame(nuke.frame()).name
