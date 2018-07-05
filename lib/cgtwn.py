# -*- coding=UTF-8 -*-
"""
cgteamwork integration for nuke.
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging

import nuke

import callback
import cgtwq
from cgtwq.helper.wlf import CGTWQHelper
from edit import CurrentViewer
from nuketools import utf8
from wlf.path import Path

LOGGER = logging.getLogger('com.wlf.cgtwn')


class Database(cgtwq.Database):
    """Optimized cgtwq database fro nuke.   """

    @classmethod
    def from_shot(cls, shot, default=None):
        """Get database from filename.

        Args:
            shot (unicode): shot name to get database.
            default (unicode, optional): Defaults to None.
                Default database name.

        Raises:
            ValueError: When no matched database,
                and `default` is not set.

        Returns:
            Database: Filename related database.
        """

        data = cgtwq.PROJECT.all().get_fields('code', 'database')
        for i in data:
            code, database = i
            if unicode(shot).startswith(code):
                return cls(database)
        if default:
            return cls(default)
        raise ValueError(
            'Can not determinate database from filename.', shot)


class Task(cgtwq.Entry):
    """Selection for single shot.  """
    # pylint: disable=too-many-ancestors

    shot = None

    def __unicode__(self):
        database = self.module.database
        project = cgtwq.PROJECT.filter(cgtwq.Filter(
            'database', database.name))['full_name'][0]
        return '{}: {}'.format(project, self.shot)

    def import_video(self, sign):
        """Import corresponse video by filebox sign.

        Args:
            sign (unicode): Server defined fileboxsign

        Returns:
            nuke.Node: Created read node.
        """

        node_name = {'animation_videos': '动画视频'}.get(sign, sign)
        n = nuke.toNode(utf8(node_name))
        if n is None:
            dir_ = self.filebox.get(sign).path
            videos = Path(dir_).glob('{}.*'.format(self.shot))
            for video in videos:
                n = nuke.nodes.Read(name=utf8(node_name))
                n['file'].fromUserText(unicode(video).encode('utf-8'))
                break
            if not n:
                raise ValueError('No matched upstream video.')
        n['frame_mode'].setValue(b'start_at')
        n['frame'].setValue(b'{:.0f}'.format(
            nuke.numvalue('root.first_frame')))
        CurrentViewer().link(n, 4, replace=False)
        return n

    @classmethod
    def from_shot(cls, shot, pipeline='合成'):
        """Get task entry from shot name.

        Args:
        shot (str): Shot name.
            pipeline (str, optional): Defaults to '合成'. Pipline name.
        """

        entry = CGTWQHelper.get_entry(shot, pipeline)
        ret = cls(entry.module, entry[0])
        ret.shot = shot

        return ret


def setup():
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(cgtwq.update_setting)
