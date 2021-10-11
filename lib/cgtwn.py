# -*- coding=UTF-8 -*-
"""
cgteamwork integration for nuke.
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging

import cast_unknown as cast
import nuke
from pathlib2_unicode import Path

import callback
import cgtwq
from cgtwq.helper.wlf import get_entry_by_file
from edit import CurrentViewer

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Text, Optional

LOGGER = logging.getLogger("com.wlf.cgtwn")


class Database(cgtwq.Database):
    """Optimized cgtwq database fro nuke."""

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

        data = cgtwq.PROJECT.select_all().get_fields("code", "database")
        for i in data:
            code, database = i
            if cast.text(shot).startswith(code):
                return cls(database)
        if default:
            return cls(default)
        raise ValueError("Can not determinate database from filename.", shot)


class Task(cgtwq.Entry):
    """Selection for single shot."""

    # pylint: disable=too-many-ancestors

    shot = None

    def __unicode__(self):
        database = self.module.database
        project = cgtwq.PROJECT.filter(cgtwq.Filter("database", database.name))[
            "full_name"
        ][0]
        return "{}: {}".format(project, self.shot)

    def import_video(self, sign):
        # type: (Text) -> Optional[nuke.Node]
        """Import corresponse video by filebox sign.

        Args:
            sign (unicode): Server defined fileboxsign

        Returns:
            Optional[nuke.Node]: Created read node.
        """

        node_name = {"animation_videos": "动画视频"}.get(sign, sign)
        n = nuke.toNode(cast.binary(node_name))
        if n is None:
            dir_ = self.filebox.get(sign).path
            videos = Path(dir_).glob("{}.*".format(self.shot))
            for video in videos:
                n = nuke.nodes.Read(name=cast.binary(node_name))
                k = n[b"file"]
                assert isinstance(k, nuke.File_Knob), k
                k.fromUserText(cast.binary(video))
                break
        if not n:
            return
        _ = n[b"frame_mode"].setValue(b"start_at")
        _ = n[b"frame"].setValue(
            cast.binary("{:.0f}".format(nuke.numvalue(b"root.first_frame"))),
        )
        CurrentViewer().link(n, 4, replace=False)
        return n

    @classmethod
    def from_shot(
        cls,
        shot,  # type: Text
        pipeline="合成",  # type: Text
    ):  # type: (...) -> Task
        """Get task entry from shot name.

        Args:
            shot (str): Shot name.
                pipeline (str, optional): Defaults to '合成'. Pipline name.
        """

        entry = get_entry_by_file(shot, pipeline)
        ret = cls(entry.module, entry[0])
        ret.shot = shot

        return ret


def setup():
    callback.CALLBACKS_ON_SCRIPT_LOAD.append(cgtwq.update_setting)
