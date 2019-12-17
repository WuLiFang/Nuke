"""Switch nuke script to use sequence.  """

import scandir
import six

from . import config, files
from .core import execute


if six.PY2:
    # patch pathlib to support unicode path
    from wlf.codectools import get_unicode
    import sys
    from wlf.path import pathlib
    _scandir = pathlib.os_scandir

    def _patched_scandir(path=six.text_type('.'), *args):
        return _scandir(get_unicode(path))
    pathlib._NormalAccessor.scandir = staticmethod(_patched_scandir)
