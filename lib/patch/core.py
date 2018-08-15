# -*- coding=UTF-8 -*-
"""Core for function patch.  """

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

import six

LOGGER = logging.getLogger(__name__)


class BasePatch(object):
    """Undoable function patcher.  """

    target = None
    _orig = None

    @classmethod
    def func(cls, *args, **kwargs):
        """Patched function.  """

        raise NotImplementedError()

    @classmethod
    def orig(cls, *args, **kwargs):
        """Shortcut for calling original function.  """

        return cls._orig[0](*args, **kwargs)

    @classmethod
    def enable(cls, is_strict=True):
        """Enabled patch.

            Args:
                is_strict(bool): If `is_strict` is True,
                    patch on not existed attr will raise a AttributeError.
        """

        assert isinstance(cls.target, six.text_type), type(cls.target)
        if cls._orig:
            LOGGER.warning('Patch already enabled: %s', cls.target)
            return
        # Save as tuple, so target function
        # will not become a unbound method of `Patch` obejct.
        cls._orig = (resolve(cls.target),)
        name, target = derive_importpath(cls.target, is_strict)
        # Need convert classmethod to a function before set it.
        setattr(target, name,
                lambda *args, **kwargs: cls.func(*args, **kwargs))  # pylint:disable = unnecessary-lambda

    @classmethod
    def disable(cls):
        """Disable patch.  """

        if not cls._orig:
            LOGGER.warning('Patch is not enabled: %s', cls.target)
            return
        name, target = derive_importpath(cls.target, True)
        setattr(target, name, cls._orig[0])
        cls._orig = None


# Module name resolve function from `pytest.monkeypatch`

def resolve(name):
    # pylint: disable=missing-docstring
    # simplified from zope.dottedname
    parts = name.split('.')

    used = parts.pop(0)
    found = __import__(used)
    for part in parts:
        used += '.' + part
        try:
            found = getattr(found, part)
        except AttributeError:
            pass
        else:
            continue
        # we use explicit un-nesting of the handling block in order
        # to avoid nested exceptions on python 3
        try:
            __import__(used)
        except ImportError as ex:
            # str is used for py2 vs py3
            expected = str(ex).split()[-1]
            if expected == used:
                raise
            else:
                raise ImportError(
                    'import error in %s: %s' % (used, ex)
                )
        found = annotated_getattr(found, part, used)
    return found


def annotated_getattr(obj, name, ann):
    # pylint: disable=missing-docstring
    try:
        obj = getattr(obj, name)
    except AttributeError:
        raise AttributeError(
            '%r object at %s has no attribute %r' % (
                type(obj).__name__, ann, name
            )
        )
    return obj


def derive_importpath(import_path, raising):
    # pylint: disable=missing-docstring
    if not isinstance(import_path, six.string_types) or "." not in import_path:
        raise TypeError("must be absolute import path string, not %r" %
                        (import_path,))
    module, attr = import_path.rsplit('.', 1)
    target = resolve(module)
    if raising:
        annotated_getattr(target, attr, ann=module)
    return attr, target
