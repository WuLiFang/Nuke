# -*- coding=UTF-8 -*-
# pyright: ignore

try:
    from concurrent.futures import * # type: ignore
except ImportError:
    from wulifang.vendor.concurrent.futures import *

