# -*- coding=UTF-8 -*-
"""File discovering that use glob-like include and exclude rules .  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import re

from wlf.path import Path


LOGGER = logging.getLogger(__name__)


def _match_rule(v, rule):
    pattern = (re.escape(rule)
               .replace("\\*\\*", ".*")
               .replace("\\*", "[^\\/]*"))
    return re.match(v, pattern)


def _search(path, exclude):
    # type: (str, list) -> None
    p = Path(path)
    for i in Path(p.parts[0]).glob(Path(*p.parts[1:]).as_posix()):
        if any(_match_rule(i.as_posix(), rule) for rule in exclude):
            continue
        yield i


def search(include, exclude):
    # type: (list, list) -> typing.Set[Path]
    """Search files

    Args:
        include (typing.List[str]): file include rules.
        exclude (typing.List[str]): file exclude rules.

    Returns:
        typing.Set[Path]: Search result
    """

    ret = set([j for i in include for j in _search(i, exclude)])
    LOGGER.info("Found files: count=%d", len(ret))
    return ret
