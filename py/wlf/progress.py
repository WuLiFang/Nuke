# -*- coding=UTF-8 -*-
"""Show progress to user.  """
try:
    import nuke
    HAS_NUKE = True
except ImportError:
    HAS_NUKE = False

__version__ = '0.1.0'


class Progress(object):

    """A Nuke progressbar compatible without nuke imported."""

    def __init__(self, name=''):
        if HAS_NUKE:
            self._task = nuke.ProgressTask(name)

    def set(self, progress=None, message=None):
        """Set progress number and message"""
        if HAS_NUKE:
            if self._task.isCancelled():
                raise RuntimeError('Cancelled.')
            if progress:
                self._task.setProgress(progress)
            if message:
                self._task.setMessage(message)
        else:
            print('{}% {}'.format(progress, message if message else ''))
