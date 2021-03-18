# -*- coding=UTF-8 -*-
"""Templates.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


from jinja2 import Environment, FileSystemLoader
import os

_ENV = Environment(
    loader=FileSystemLoader(
        os.path.dirname(__file__)
    ),
)


def render(name, context=None):
    template = _ENV.get_template(name)
    return template.render(context)
