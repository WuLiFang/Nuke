# -*- coding=UTF-8 -*-
"""
site customize script.
https://docs.python.org/2/tutorial/appendix.html#the-customization-modules
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

def _enable_windows_unicode_console():
    import sys
    if sys.platform != 'win32':
        return
    import win_unicode_console
    import warnings
    warnings.filterwarnings("ignore", "readline hook consumer may assume they are the same", RuntimeWarning)
    win_unicode_console.enable()

_enable_windows_unicode_console()
