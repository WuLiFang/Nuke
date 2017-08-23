# -*- coding=UTF-8 -*-
"""Show progress to user.  """
try:
    import nuke
    HAS_NUKE = True
except ImportError:
    HAS_NUKE = False

__version__ = '0.1.1'


class Progress(object):

    """A Nuke progressbar compatible without nuke imported."""

    def __init__(self, name=''):
        if HAS_NUKE:
            self._task = nuke.ProgressTask(name)

    def set(self, progress=None, message=None):
        """Set progress number and message"""

        if self.is_cancelled():
            raise CancelledError

        if HAS_NUKE:
            if progress:
                self._task.setProgress(progress)
            if message:
                self._task.setMessage(message)
        else:
            print('{}% {}'.format(progress, message if message else ''))

    def is_cancelled(self):
        """Return if cancel button been pressed.  """

        if HAS_NUKE:
            return self._task.isCancelled()

        return False


class CancelledError(Exception):
    """Indicate user pressed CancelButton.  """

    def __str__(self):
        return 'Cancelled. '
