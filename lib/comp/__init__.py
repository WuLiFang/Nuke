# -*- coding=UTF-8 -*-
"""WuLiFang Comp package.  """

from __future__ import absolute_import, unicode_literals, print_function

_argv = __import__('sys').argv  # Backup argv

from .base import Comp, FootageError, RenderError, render_png
from .precomp import Precomp
from .batch import BatchComp
