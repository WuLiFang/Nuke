# -*- coding=UTF-8 -*-
# Copyright (c) 2021 WuLiFang studio.
"""
typing for nuke python api.  

https://learn.foundry.com/nuke/developers/100/pythonreference/
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union, overload

import six

ADD_VIEWS = 0
AFTER_CONST = 21
AFTER_LINEAR = 22
ALL = 1
ALWAYS_SAVE = 1048576
BEFORE_CONST = 19
BEFORE_LINEAR = 20
BREAK = 18
CATMULL_ROM = 3
CONSTANT = 1
CUBIC = 4
DISABLED = 128
DONT_CREATE_VIEWS = 2
DONT_SAVE_TO_NODEPRESET = 549755813888
DO_NOT_WRITE = 512
ENDLINE = 8192
EXE_PATH: six.binary_type
EXPAND_TO_WIDTH = 68719476736
EXPRESSIONS = 1
FLOAT = 5
FONT = 4
GEO = 16
GUI = False
HIDDEN_INPUTS = 4
HORIZONTAL = 17
IMAGE = 1
INPUTS = 2
INT16 = 3
INT8 = 2
INTERACTIVE = True
INVALIDHINT = -1
INVISIBLE = 1024
KNOB_CHANGED_RECURSIVE = 134217728
LINEAR = 2
LOG = 4
MATCH_CLASS = 0
MATCH_COLOR = 2
MATCH_LABEL = 1
MONITOR = 0
NODIR = 2
NO_ANIMATION = 256
NO_CHECKMARKS = 1
NO_MULTIVIEW = 1073741824
NO_POSTAGESTAMPS = False
NO_UNDO = 524288

NUKE_VERSION_DATE: six.binary_type
NUKE_VERSION_MAJOR: int
NUKE_VERSION_MINOR: int
NUKE_VERSION_PHASE: six.binary_type
NUKE_VERSION_PHASENUMBER: int
NUKE_VERSION_RELEASE: int
NUKE_VERSION_STRING: six.binary_type
NUM_CPUS: int
NUM_INTERPOLATIONS = 5
PLUGIN_EXT: six.binary_type
PREPEND = 8
PROFILE_ENGINE = 3
PROFILE_REQUEST = 2
PROFILE_STORE = 0
PROFILE_VALIDATE = 1
PYTHON = 32
READ_ONLY = 268435456
REPLACE = 1
REPLACE_VIEWS = 1
SAVE_MENU = 33554432
SCRIPT = 2
SMOOTH = 0
STARTLINE = 4096
STRIP_CASCADE_PREFIX = 4
TABBEGINCLOSEDGROUP = 2
TABBEGINGROUP = 1
TABENDGROUP = -1
TABKNOB = 0
THREADS = 8
TO_SCRIPT = 1
TO_VALUE = 2
USER_SET_SLOPE = 16
VIEWER = 1
VIEW_NAMES: six.binary_type
WRITE_ALL = 8
WRITE_NON_DEFAULT_ONLY = 16
WRITE_USER_KNOB_DEFS = 4
__package__ = 'nuke'
afterBackgroundFrameRenders: list
afterBackgroundRenders: list
afterFrameRenders: dict
afterRenders: dict
autoSaveDeleteFilters: Dict[six.binary_type, Callable]
autoSaveFilters: Dict[six.binary_type, Callable]
autoSaveRestoreFilters: Dict[six.binary_type, Callable]
autolabels: dict
beforeBackgroundRenders: list
beforeFrameRenders: dict
beforeRenders: dict
defaultLUTMappers: dict
env = dict
filenameFilters: dict
knobChangeds = Dict[six.binary_type, Callable]
nodes = Nodes
onCreates = Dict[six.binary_type, Callable]
onDestroys: dict
onScriptCloses: dict
onScriptLoads: dict
onScriptSaves: dict
onUserCreates: Dict[six.binary_type, Callable]
rawArgs: List[six.binary_type]
renderProgresses: dict
untitled: six.binary_type
updateUIs: dict
validateFilenames: dict


class Knob:
    """
    A modifiable control that appears (unless hidden) in the panel for a node.
    This is a base class that specific knob types inherit from.
    Knobs can be animated, have expressions, be disabled or hidden and more.
    """

    def Class(self) -> six.binary_type:
        """Class name.  """
        ...

    def __init__(*args: ..., **kwargs: ...):
        """x.__init__(...) initializes x; see help(type(x)) for signature.  """
        ...

    def clearAnimated(self, c=...):
        """Clear animation for channel 'c'.  """
        ...

    def clearFlag(self, f):
        """Clear flag.  """
        ...

    def critical(self, message: six.binary_type):
        ...

    def debug(self, message: six.binary_type):
        ...

    def error(self, message: six.binary_type):
        ...

    def enabled(self) -> bool:
        ...

    def fromScript(self, script: six.binary_type) -> bool:
        """
        fromScript(...)
        Initialise from script.
        """
        ...

    def fullyQualifiedName(self, channel=-1) -> bool:
        """
        Returns the fully-qualified name of the knob within the node.
        """
        ...

    def getDerivative(self, channel=-1) -> bool:
        """
        Returns the fully-qualified name of the knob within the node.
        """
        ...

    def getFlag(self, f) -> bool:
        """
        Returns whether the input flag is set.
        """
        ...

    def value(self, c=...) -> Any:
        """
        Return value at the current frame for channel 'c'.
        """
    ...


class Node:
    def __getitem__(self, name: six.binary_type) -> Knob:
        """Get knob by name. """

    def Class(self) -> six.binary_type:
        """Class of node.  """
        ...

    def bbox(self) -> Tuple[int, int, int, int]:
        """Bounding box of the node.  """
        ...

    def firstFrame(self) -> int:
        """First frame in frame range for this node.  """
        ...

    def lastFrame(self) -> int:
        """Last frame in frame range for this node.  """
        ...

    def metadata(self, key: six.binary_type, time: int = ..., view: six.binary_type = ...) -> Union[six.binary_type, dict]:
        """
        Return the metadata item for key on this node
        at current output context, or at optional time and view.
        """
        ...

    def name(self) -> six.binary_type:
        ...
    ...


class Nodes:
    ...


class FrameRange:
    """A frame range, with an upper and lower bound and an increment.  """
    @overload
    def __init__(self, first: int, last: int, increment: int) -> None: ...
    @overload
    def __init__(self, s: six.binary_type) -> None: ...
    def __iter__(self) -> int: ...
    def __str__(self) -> six.binary_type: ...

    def first(self) -> int:
        """return the first frame of the range.  """
        ...

    def frames(self) -> int:
        """return the numbers of frames defined in the range.  """
        ...

    def getFrame(self, n: int) -> int:
        """
        return the frame according to the index,
        parameter n must be between 0 and frames().  
        """
        ...

    def increment(self) -> int:
        """return the increment between two frames.  """
        ...

    def isInRange(self, n) -> bool:
        """return if the frame is inside the range.  """
        ...

    def last(self) -> int:
        """return the last frame of the range.  """
        ...

    def maxFrame(self) -> int:
        """return the maximun frame define in the range.   """
        ...

    def minFrame(self) -> int:
        """return the minimun frame define in the range.   """
        ...

    def next(self) -> FrameRange:
        """the next value, or raise StopIteration.   """
        ...

    def setFirst(self, n: int) -> None:
        """set the first frame of the range.   """
        ...

    def setIncrement(self, n: int) -> None:
        """set the increment between two frames.   """
        ...

    def setLast(self, n: int) -> None:
        """set the last frame of the range.   """
        ...

    def stepFrame(self) -> int:
        """return the absolute increment between two frames.  """
        ...


class Group(Node):
    ...


class Root(Group):
    ...


class FrameRanges:
    """
    A sequence of FrameRange objects with convenience functions
    for iterating over all frames in all ranges.
    """

    def __init__(self, o: Union[six.binary_type, List[FrameRange], List[six.binary_type], List[int]]) -> None: ...
    def __str__(self) -> six.binary_type: ...
    def __iter__(self) -> FrameRange: ...

    def add(self, r: FrameRange) -> None:
        """add a new frame range.  """
        ...

    def clear(self) -> None:
        """reset all store frame ranges.  """
        ...

    def compact(self) -> None:
        """compact all the frame ranges.  """
        ...

    def getRange(self) -> FrameRange:
        """return a range from the list.   """
        ...

    def maxFrame(self) -> int:
        """get maximun frame of all ranges.   """
        ...

    def minFrame(self) -> int:
        """get minimun frame of all ranges.   """
        ...

    def next(self) -> FrameRange:
        """the next value, or raise StopIteration.   """
        ...

    def size(self) -> int:
        """return the ranges number.  """
        ...

    def toFrameList(self) -> List[int]:
        """return a list of frames in a vector.   """
        ...


def thisNode() -> Node:
    """Return the current context node.  """
    ...


def thisKnob() -> Optional[Knob]:
    """Returns the current context knob if any.  """
    ...


def value(name: six.binary_type, default: six.binary_type = None) -> six.binary_type:
    """The value function returns the current value of a knob.  """
    ...


def addAutolabel(call: Callable, args: tuple = (), kwargs: dict = {}, nodeClass: six.binary_type = b'*'):
    """
    Add code to execute on every node to produce the text to draw on it in the DAG.
    Any value other than None is converted to a six.binary_typeing and used as the text.
    None indicates that previously-added functions should be tried
    """
    ...


def filename(node: Node = None, i: int = None) -> Optional[six.binary_type]:
    """
    Return the filename(s) this node or group is working with.

    For a Read or Write operator (or anything else with a filename knob)
    this will return the current filename, based on the root.proxy settings
    and which of the fullsize/proxy filenames are filled in.
    All expansion of commands and variables is done
    However by default it will still have %%04d sequences in it,
    use REPLACE to get the actual filename with the current frame number.

    If the node is a group, a search is done for executable (i.e. Write)
    operators and the value from each of them is returned.
    This will duplicate the result of calling execute() on the group.

    Parameters:
        node - Optional node.
        i - Optional nuke.REPLACE.
            Will replace %%04d style sequences with the current frame number.
    Returns: six.binary_type
        Filename, or None if no filenames are found.
    """
    ...


def message(prompt: six.binary_type) -> None:
    """
    Show an info dialog box.
    Pops up an info box (with a 'i' and the text message)
    and waits for the user to hit the OK button.

    Parameters:
        prompt - Present user with this message.
    """
    ...


def warning(message: six.binary_type) -> None:
    """
    Puts the message into the error console, treating it like a warning.

    Parameters:
        message - String parameter.
    """
    ...


def scriptName() -> six.binary_type:
    """Return the current script's file name.  """
    ...


def allNodes(filter: six.binary_type = None, group: Group = None, recurseGroups: bool = False) -> List[Node]:
    """
    List of all nodes in a group.
    If you need to get all the nodes in the script from a context which has no child nodes,
    for instance a control panel, use nuke.root().nodes().

    Parameters:
        filter - Optional. Only return nodes of the specified class.
        group - Optional. If the group is omitted the current group 
            (ie the group the user picked a menu item from the toolbar of) is used.
        recurseGroups - Optional. If True, will also return all child nodes within any group nodes.
            This is done recursively and defaults to False.
    """
    ...


def root() -> Root:
    """
    Get the DAG's root node. Always succeeds.

    Returns: node
        The root node. This will never be None.
    """
    ...
