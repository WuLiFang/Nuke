# -*- coding: UTF-8 -*-
"""Handle dropdata in nuke."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import base64
import logging
import os
import re

import nuke

import callback
from edit import clear_selection
from wlf.codectools import get_encoded as e
from wlf.codectools import get_unicode as u
from wlf.codectools import is_ascii
from wlf.progress import CancelledError, progress

LOGGER = logging.getLogger('com.wlf.callback')


def dropdata_handler(mime_type, data, from_dir=False):
    """Handling dropdata."""

    LOGGER.debug('Handling dropdata: %s %s', mime_type, u(data))
    if mime_type != 'text/plain':
        return
    data = u(data)

    def _isdir():
        if os.path.isdir(e(data)):
            _dirname = data.replace('\\', '/')
            filenames = nuke.getFileNameList(e(_dirname, 'UTF-8'))
            try:
                for filename in progress(filenames):
                    dropdata_handler(
                        mime_type, '{}/{}'.format(_dirname, filename),
                        from_dir=True)
            except CancelledError:
                pass
            return True

    def _ignore():
        ignore_pat = (r'thumbs\.db$', r'.*\.lock$', r'.* - 副本\b')
        filename = os.path.basename(data)
        for pat in ignore_pat:
            if re.match(u(pat), u(filename), flags=re.I | re.U):
                return True
        if data.endswith('.mov') and not is_ascii(data):
            nuke.createNode(
                'StickyNote', b'autolabel {{\'<div align="center">\'+autolabel()+\'</div>\'}} '
                b'label {{{}\n\n<span style="color:red;text-align:center;font-weight:bold">'
                b'mov格式使用非英文路径将可能导致崩溃</span>}}'.format(e(data, 'utf-8')), inpanel=False)
            return True

    def _file_protocol():
        match = re.match(r'file://+([^/].*)', data)
        if match:
            _data = match.group(1)
            try:
                _data = base64.b64decode(_data)
            except TypeError:
                pass
            return dropdata_handler(mime_type, _data, from_dir=True)

    def _fbx():
        if data.endswith('.fbx'):
            n = nuke.createNode(
                'Camera2',
                b'read_from_file True '
                b'frame_rate 25 '
                b'suppress_dialog True '
                b'label {'
                b'导入的摄像机：\n'
                b'[basename [value file]]\n}')
            n.setName('Camera_3DEnv_1')
            n['file'].fromUserText(data)
            if nuke.expression('{}.animated'.format(n.name())):
                n['read_from_file'].setValue(False)

            n = nuke.createNode('ReadGeo2')
            n['file'].fromUserText(data)
            n['all_objects'].setValue(True)
            return True

    def _vf():
        if data.endswith('.vf'):
            nuke.createNode(
                'Vectorfield',
                'vfield_file "{data}" '
                'file_type vf '
                'label {{[value this.vfield_file]}}'.format(data=data.replace('\\', '/')))
            return True

    def _nk():
        if data.endswith('.nk'):
            nuke.scriptReadFile(data)
            return True

    def _video():
        if data.endswith(('.mov', '.mp4', '.avi')):

            n = nuke.createNode('Read', 'file "{}"'.format(data))
            if n.hasError():
                n['disable'].setValue(True)
            return True

    def _from_dir():
        if from_dir:
            n = nuke.createNode(
                'Read', 'file "{}"'.format(data), inpanel=False)
            if n.hasError():
                n['disable'].setValue(True)
            return True

    clear_selection()
    for func in (_isdir, _ignore, _file_protocol, _video, _vf, _fbx, _from_dir, _nk):
        if func():
            return True


def setup():
    callback.CALLBACKS_ON_DROP_DATA.append(dropdata_handler)
