# -*- coding=UTF-8 -*-
"""Data models.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
from collections import namedtuple

from jinja2 import Environment, FileSystemLoader

from . import core

LOGGER = logging.getLogger(__name__)


class MissingFramesDict(dict):
    """Missing frames data.  """

    def __str__(self):
        rows = ['| Filename | MissingFrames |:']
        for k in sorted(self):
            rows.append('| {} | {} |'.format(k, self[k]))
        return '\n'.join(rows)

    def as_html(self):
        """Convert the data to html page.  """
        env = Environment(loader=FileSystemLoader(core.TEMPLATES_DIR))
        template = env.get_template('dropframes.html')
        return template.render(data=self.items())
