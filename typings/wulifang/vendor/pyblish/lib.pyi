# -*- coding=UTF-8 -*-
# This typing file was generated by typing_from_help.py
# pyright: reportUndefinedVariable=information,reportUnusedImport=false
"""
wulifang.vendor.pyblish.lib

"""

import typing

class ItemList(__builtin__.list):
    """
    List with keys

    Raises:
        KeyError is item is not in list

    Example:
        >>> Obj = type("Object", (object,), {})
        >>> obj = Obj()
        >>> obj.name = "Test"
        >>> l = ItemList(key="name")
        >>> l.append(obj)
        >>> l[0] == obj
        True
        >>> l["Test"] == obj
        True
        >>> try:
        ...   l["NotInList"]
        ... except KeyError:
        ...   print(True)
        True
        >>> obj == l.get("Test")
        True
        >>> l.get("NotInList") == None
        True
    """

    __dict__: ...
    """
    dictionary for instance variables (if defined)
    """

    __weakref__: ...
    """
    list of weak references to the object (if defined)
    """

    def __getitem__(self, index):
        """
        """
        ...

    def __init__(self, key, object=[]):
        """
        """
        ...

    def get(self, key, default=None):
        """
        """
        ...

    ...

class MessageHandler(logging.Handler):
    def __init__(self, records, *args, **kwargs):
        """
        """
        ...

    def emit(self, record):
        """
        """
        ...

    ...

class classproperty(__builtin__.object):
    __dict__: ...
    """
    dictionary for instance variables (if defined)
    """

    __weakref__: ...
    """
    list of weak references to the object (if defined)
    """

    def __get__(self, instance, owner):
        """
        """
        ...

    def __init__(self, getter):
        """
        """
        ...

    ...

def deprecated(func):
    """
    Deprecation decorator
    Attach this to deprecated functions or methods.
    """
    ...


def emit(signal, **kwargs):
    """
    Trigger registered callbacks
    Keyword arguments are passed from caller to callee.
    Arguments:
        signal (string): Name of signal emitted
    Example:
        >>> import sys
        >>> from . import plugin
        >>> plugin.register_callback(
        ...   "mysignal", lambda data: sys.stdout.write(str(data)))
        ...
        >>> emit("mysignal", data={"something": "cool"})
        {'something': 'cool'}
    """
    ...


def extract_traceback(exception, fname=None):
    """
    Inject current traceback and store in exception.traceback.
    Also storing the formatted traceback on exception.formtatted_traceback.
    Arguments:
        exception (Exception): Exception object
        fname (str): Optionally provide a file name for the exception.
            This is necessary to inject the correct file path in the traceback.
            If plugins are registered through `api.plugin.discover`, they only
            show "<string>" instead of the actual source file.
    """
    ...


def get_formatter():
    """
    Return a default Pyblish formatter for logging
    Example:
        >>> import logging
        >>> log = logging.getLogger("myLogger")
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(get_formatter())
    """
    ...


def inrange(number, base, offset=0.5):
    """
    Evaluate whether `number` is within `base` +- `offset`
    Lower bound is *included* whereas upper bound is *excluded*
    so as to allow for ranges to be stacked up against each other.
    For example, an offset of 0.5 and a base of 1 evenly stacks
    up against a base of 2 with identical offset.
    Arguments:
        number (float): Number to consider
        base (float): Center of range
        offset (float, optional): Amount of offset from base
    Usage:
        >>> inrange(0, base=1, offset=0.5)
        False
        >>> inrange(0.4, base=1, offset=0.5)
        False
        >>> inrange(1.4, base=1, offset=0.5)
        True
        >>> # Lower bound is included
        >>> inrange(0.5, base=1, offset=0.5)
        True
        >>> # Upper bound is excluded
        >>> inrange(1.5, base=1, offset=0.5)
        False
    """
    ...


def log(cls):
    """
    Decorator for attaching a logger to the class `cls`
    Loggers inherit the syntax {module}.{submodule}
    Example
        >>> @log
        ... class MyClass(object):
        ...     pass
        >>>
        >>> myclass = MyClass()
        >>> myclass.log.info('Hello World')
    """
    ...


def main_package_path():
    """
    Return path of main pyblish package
    """
    ...


def parse_environment_paths(paths):
    """
    Given a (semi-)colon separated string of paths, return a list
    Example:
        >>> import os
        >>> parse_environment_paths("path1" + os.pathsep + "path2")
        ['path1', 'path2']
        >>> parse_environment_paths("path1" + os.pathsep)
        ['path1', '']
    Arguments:
        paths (str): Colon or semi-colon (depending on platform)
            separated string of paths.
    Returns:
        list of paths as string.
    """
    ...


def setup_log(root='pyblish', level=10):
    """
    Setup a default logger for Pyblish
    Example:
        >>> log = setup_log()
        >>> log.info("Hello, World")
    """
    ...


def time():
    """
    Return ISO formatted string representation of current UTC time.
    """
    ...


__all__: ...
"""
['ItemList', 'MessageHandler', '__builtins__', '__doc__', '_...
"""

_registered_callbacks: dict
"""
{}
"""

