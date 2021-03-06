# -*- coding=UTF-8 -*-
"""Concurrent executor.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from concurrent import futures

EXECUTOR = futures.ThreadPoolExecutor()
