# -*- coding=UTF-8 -*-
# This typing file was generated by typing_from_help.py
# pyright: reportUndefinedVariable=information,reportUnusedImport=false
"""
wulifang.vendor.pyblish.logic - Shared processing logic

"""

import typing

class TestFailed(Exception):
    __weakref__: ...
    """
    list of weak references to the object (if defined)
    """

    def __init__(self, msg, vars):
        """
        """
        ...

    ...

class Validator(Plugin):
    """
    Validate/check/test individual instance for correctness.
    """

    __contextEnabled__: ...
    """
    """

    __instanceEnabled__: ...
    """
    """

    __pre11__: ...
    """
    """

    log: ...
    """
    """

    order: ... = 1
    """
    """

    def id(self):
        """
        alias of 'df0dec87-fc6d-4ad5-873d-30a20041c1d1'
        """
        ...

    ...

def Iterator(plugins, context, state=None, targets=None):
    """
    Primary iterator
    This is the brains of publishing. It handles logic related
    to which plug-in to process with which Instance or Context,
    in addition to stopping when necessary.
    Arguments:
        plugins (list): Plug-ins to consider
        context (list): Instances to consider
        state (dict): Mutable state
        targets (list, optional): Targets to include for publish session.
    """
    ...


def _extract_traceback(exception):
    """
    Append traceback to `exception`
    This function safely extracts a traceback while being
    careful not to leak memory.
    Arguments:
        exception (Exception): Append traceback to here
            as "traceback" attribute.
    """
    ...


def default_test(**vars):
    """
    Evaluate whether or not to continue processing
    The test determines whether or not to proceed from one
    plug-in to the next. The `vars` are updated everytime
    a plug-in is about to be processed with information about
    the upcoming plug-in.
    Returning any value means failure, whereas 0, False and None
    represents success. Similar to return/exit codes. You can provide
    a message along with a failure, such as specifying why the test
    failed. The message can then be used by process handlers,
    such as a GUI.
    You can provide your own test by registering it, see example below.
    Contents of `vars`:
        nextOrder (int): Order of next plugin
        ordersWithError (list): Orders at which an error has occured
    """
    ...


def deregister_gui(package):
    """
    """
    ...


def deregister_test():
    """
    Restore default test
    """
    ...


def instances_by_plugin(instances, plugin):
    """
    Return compatible instances `instances` to plugin `plugin`
    Return instances as they correspond to a plug-in, given
    an algorithm. The algorithm is determined by the `Plugin.match`
    When `match == Subset`, families of an instance must be a
    subset of families supported by a plug-in.
    Arguments:
        instances (list): List of instances
        plugin (Plugin): Plugin with which to compare against
    Returns:
        List of compatible instances
    Invariant:
        Order of remaining plug-ins must remain the same
    """
    ...


def plugins_by_families(plugins, families):
    """
    Same as :func:`plugins_by_family` except it takes multiple families
    Arguments:
        plugins (list): List of plugins
        families (list): Families with which to compare against
    Returns:
        List of compatible plugins.
    """
    ...


def plugins_by_family(plugins, family):
    """
    Convenience function to :func:`plugins_by_families`
    Arguments:
        plugins (list): List of plugins
        family (str): Family with which to compare against
    Returns:
        List of compatible plugins.
    """
    ...


def plugins_by_host(plugins, host):
    """
    Return compatible plugins `plugins` to host `host`
    Arguments:
        plugins (list): List of plugins
        host (str): Host with which compatible plugins are returned
    Returns:
        List of compatible plugins.
    """
    ...


def plugins_by_instance(plugins, instance):
    """
    Conveinence function for :func:`plugins_by_family`
    Arguments:
        plugins (list): Plug-ins to assess
        instance (Instance): Instance with which to compare against
    Returns:
        List of compatible plugins
    """
    ...


def plugins_by_targets(plugins, targets):
    """
    Reutrn compatible plugins `plugins` to targets `targets`
    Arguments:
        plugins (list): List of plugins
        targets (list): List of targets with which to compare against
    Returns:
        List of compatible plugins.
    """
    ...


def register_gui(package):
    """
    Register a default GUI for Pyblish
    The argument `package` must refer to an available Python
    package with access to a `.show` member function taking no
    arguments. E.g.
    def show():
        pass
    This function is called whenever the default GUI
    is activated.
    Multiple GUIs:
        You may register more than one GUI, in which case each
        is tried in turn until a functioning match is found.
        For example, if both Pyblish QML and Pyblish Lite are
        registered, but Pyblish QML is not installed, then
        Pyblish Lite would appear as a "fallback".
    Arguments:
        package (str): Name of Python package with .show function.
    """
    ...


def register_test(test):
    """
    Register test used to determine when to abort processing
    Arguments:
        test (callable): Called with argument `vars` and returns
            either True or False. True means to continue,
            False to abort.
    Example:
        >>> # Register custom test
        >>> def my_test(**vars):
        ...   return 1
        ...
        >>> register_test(my_test)
        >>>
        >>> # Run test
        >>> if my_test(order=1, ordersWithError=[]):
        ...   print("Test passed")
        Test passed
        >>>
        >>> # Restore default
        >>> deregister_test()
    """
    ...


def registered_guis():
    """
    Return registered GUIs
    """
    ...


def registered_targets():
    """
    Return the currently registered targets
    """
    ...


def registered_test():
    """
    Return the currently registered test
    """
    ...


Exact: int = 4

Intersection: int = 1

Subset: int = 2

__all__: ...
"""
['Exact', 'Intersection', 'Iterator', 'Subset', 'TestFailed'...
"""

_algorithms: ...
"""
{1: <function <lambda>>, 2: <function <lambda>>, 4: <fun...
"""

_registered_gui: list
"""
[]
"""

_registered_test: dict
"""
{}
"""

log: ...
"""
<logging.Logger object>
"""

