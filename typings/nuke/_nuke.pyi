# -*- coding=UTF-8 -*-
# Copyright (c) 2021 WuLiFang studio.
"""
typing for nuke python api.

https://learn.foundry.com/nuke/developers/100/pythonreference/
"""

import io
from typing import Any, Callable, Dict, IO, List, Literal, Optional, Tuple, TypeVar, Union, overload

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
        """x.__init__() initializes x; see help(type(x)) for signature.  """
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
        fromScript()
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

    def metadata(self, key: six.binary_type, time: int = ..., view: six.binary_type = ...) -> Union[six.binary_type, dict, None]:
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


class ViewerWindow:
    ...

class Dock:
    ...

class Pane:
    ...
class Menu:
    ...
class ToolBar:
    ...


def __filterNames(name):
    ...


def activeViewer() -> ViewerWindow:
    """
    Return an object representing the active Viewer panel.
    """
    ...


def addAfterBackgroundFrameRender(call, args=(), kwargs={}):
    """
    Add code to execute after each frame of a background render.
    """
    ...


def addAfterBackgroundRender(call, args=(), kwargs={}):
    """
    Add code to execute after any background renders.
    """
    ...


def addAfterFrameRender(call, args=(), kwargs={}, nodeClass='Write'):
    """
    Add code to execute after each frame of a render
    """
    ...


def addAfterRecording(call, args=(), kwargs={}, nodeClass='Viewer'):
    """
    Add code to execute after viewer recording
    """
    ...


def addAfterRender(call, args=(), kwargs={}, nodeClass='Write'):
    """
    Add code to execute after any renders
    """
    ...


def addAfterReplay(call, args=(), kwargs={}, nodeClass='Viewer'):
    """
    Add code to execute after viewer replay
    """
    ...


def addAutoSaveDeleteFilter(filter) -> None:
    """
    Add a function to modify the autosave filename before Nuke attempts 
          delete the autosave file.
    """
    ...


def addAutoSaveFilter(filter) -> None:
    """
    Add a function to modify the autosave filename before Nuke saves the 
          current script on an autosave timeout.
    """
    ...


def addAutoSaveRestoreFilter(filter) -> None:
    """
    Add a function to modify the autosave restore file before Nuke 
          attempts to restores the autosave file.
    """
    ...


def addAutolabel(call, args=(), kwargs={}, nodeClass='*'):
    """
    Add code to execute on every node to produce the text to draw on it 
          in the DAG.
    """
    ...


def addBeforeBackgroundRender(call, args=(), kwargs={}):
    """
    Add code to execute before starting any background renders.
    """
    ...


def addBeforeFrameRender(call, args=(), kwargs={}, nodeClass='Write'):
    """
    Add code to execute before each frame of a render
    """
    ...


def addBeforeRecording(call, args=(), kwargs={}, nodeClass='Viewer'):
    """
    Add code to execute before viewer recording
    """
    ...


def addBeforeRender(call, args=(), kwargs={}, nodeClass='Write'):
    """
    Add code to execute before starting any renders
    """
    ...


def addBeforeReplay(call, args=(), kwargs={}, nodeClass='Viewer'):
    """
    Add code to execute before viewer replay
    """
    ...


def addDefaultColorspaceMapper(call, args=(), kwargs={}, nodeClass='*'):
    """
    Add a function to modify default colorspaces before Nuke passes them 
          to Readers or Writers.
    """
    ...


def addFavoriteDir(name, directory, type, icon, tooltip, key) -> None:
    """
    Add a path to the file choosers favorite directory list.
    """
    ...


def addFilenameFilter(call, args=(), kwargs={}, nodeClass='*'):
    """
    Add a function to modify filenames before Nuke passes them to the 
          operating system.
    """
    ...


def addFormat(s) -> Optional[six.binary_type]:
    """
    Create a new image format, which will show up on the pull-down menus 
          for image formats.
    """
    ...


def addKnobChanged(call, args=(), kwargs={}, nodeClass='*', node=None):
    """
    Add code to execute when the user changes a knob The knob is availble
          in nuke.thisKnob() and the node in nuke.thisNode().
    """
    ...


def addNodePresetExcludePaths(paths) -> None:
    """
    @param paths Sequence of paths to exclude Adds a list of paths that 
          will be excluded from Node preset search paths.
    """
    ...


def addOnCreate(call, args=(), kwargs={}, nodeClass='*'):
    """
    Add code to execute when a node is created or undeleted
    """
    ...


def addOnDestroy(call, args=(), kwargs={}, nodeClass='*'):
    """
    Add code to execute when a node is destroyed
    """
    ...


def addOnScriptClose(call, args=(), kwargs={}, nodeClass='Root'):
    """
    Add code to execute before a script is closed
    """
    ...


def addOnScriptLoad(call, args=(), kwargs={}, nodeClass='Root'):
    """
    Add code to execute when a script is loaded
    """
    ...


def addOnScriptSave(call, args=(), kwargs={}, nodeClass='Root'):
    """
    Add code to execute before a script is saved
    """
    ...


def addOnUserCreate(call, args=(), kwargs={}, nodeClass='*'):
    """
    Add code to execute when user creates a node
    """
    ...


def addRenderProgress(call, args=(), kwargs={}, nodeClass='Write'):
    """
    Add code to execute when the progress bar updates during any renders
    """
    ...


def addSequenceFileExtension(fileExtension):
    """
    Adds the input file extension to the list of extensions that will get
          displayed as sequences in the file browser.
    """
    ...


def addToolsetExcludePaths(paths) -> None:
    """
    @param paths Sequence of paths to exclude Adds a list of paths that 
          will be excluded from Toolset search paths.
    """
    ...


def addUpdateUI(call, args=(), kwargs={}, nodeClass='*'):
    """
    Add code to execute on every node when things change.
    """
    ...


def addValidateFilename(call, args=(), kwargs={}, nodeClass='Write'):
    """
    Add a function to validate a filename in Write nodes.
    """
    ...


def addView(s) -> None:
    """
    Deprecated.
    """
    ...


def afterBackgroundFrameRender(context):
    ...


def afterBackgroundRender(context):
    ...


def afterFrameRender():
    ...


def afterRecording():
    ...


def afterRender():
    ...


def afterReplay():
    ...


def allNodes(filter, group) -> List:
    """
    List of all nodes in a group.
    """
    ...


def animation(object, *commands) -> None:
    """
    Does operations on an animation curve.
    """
    ...


def animationEnd() -> float:
    """
    Returns the last frame (or x value) for the currently selected 
          animations.
    """
    ...


def animationIncrement() -> float:
    """
    Returns a recommended interval between samples of the currently 
          selected animation.
    """
    ...


def animationStart() -> float:
    """
    Returns the starting frame (or x value) for the currently selected 
          animations.
    """
    ...


def animations() -> tuple:
    """
    Returns a list of animatable things the user wants to work on.
    """
    ...


def applyPreset(nodeName, presetName) -> None:
    """
    Applies a given preset to the current node.
    """
    ...


def applyUserPreset(nodeName, presetName) -> None:
    """
    Applies a given user preset to the current node.
    """
    ...


def ask(prompt) -> bool:
    """
    Show a Yes/No dialog.
    """
    ...


def askWithCancel(prompt) -> bool:
    """
    Show a Yes/No/Cancel dialog.
    """
    ...


def autoSaveDeleteFilter(filename):
    """
    Internal function.
    """
    ...


def autoSaveFilter(filename):
    """
    Internal function.
    """
    ...


def autoSaveRestoreFilter(filename):
    """
    Internal function.
    """
    ...


def autolabel():
    ...


def autoplace(n) -> None:
    """
    Deprecated.
    """
    ...


def autoplaceSnap(n) -> None:
    """
    Move node to the closest grid position.
    """
    ...


def beforeBackgroundRender(context):
    ...


def beforeFrameRender():
    ...


def beforeRecording():
    ...


def beforeRender():
    ...


def beforeReplay():
    ...


def cacheUsage() -> int:
    """
    Get the total amount of memory currently used by the cache.
    """
    ...


def canCreateNode(name) -> bool:
    """
    This function can be used to determine whether it is possible to 
          create a node with the specified node class.
    """
    ...


def cancel() -> None:
    """
    Cancel an in-progress operation.
    """
    ...


def center() -> Tuple[int, int]:
    """
    Return the center values of a group's display, these values are 
          suitable to be passed to nuke.zoom as the DAG center point.
    """
    ...


def choice(title, prompt, options, default=0) -> int:
    """
    Shows a dialog box with the given title and prompt text, and a combo 
          box containing the given options.
    """
    ...


def clearDiskCache() -> None:
    """
    Clear the disk cache of all files.
    """
    ...


def clearRAMCache() -> None:
    """
    Clear the RAM cache of all files.
    """
    ...


def clone(n, args, inpanel) -> Node:
    """
    Create a clone node that behaves identical to the original.
    """
    ...


def cloneSelected(action) -> bool:
    """
    This makes a clone of all selected nodes, preserving connections 
          between them, and makes only the clones be selected.
    """
    ...


def collapseToGroup(show=True) -> Group:
    """
    Moves the currently selected nodes to a new group, maintaining their 
          previous connections.
    """
    ...


def connectNodes() -> None:
    """
    Deprecated.
    """
    ...


def connectViewer(inputNum, node) -> None:
    """
    Connect a viewer input to a node.
    """
    ...


def createNode(node, args, inpanel) -> Node:
    """
    Creates a node of the specified type and adds it to the DAG.
    """
    ...


def createScenefileBrowser(fileName, nodeName) -> None:
    """
    Pops up a scene browser dialog box.
    """
    ...


def createToolset(filename=None, overwrite=-1, rootPath=None) -> None:
    """
    Creates a tool preset based on the currently selected nodes.
    """
    ...


def critical(message) -> None:
    """
    Puts the message into the error console, treating it like an error.
    """
    ...


def debug(message) -> None:
    """
    Puts the message into the error console, treating it like a debug 
          message, which only shows up when the verbosity level is high enough.
    """
    ...


def defaultColorspaceMapper(colorspace, dataTypeHint):
    """
    Called by libnuke.
    """
    ...


def defaultFontPathname() -> str:
    """
    Get the path to Nukes default font.
    """
    ...


def defaultNodeColor(s) -> int:
    """
    Get the default node colour.
    """
    ...


def delete(n) -> None:
    """
    The named node is deleted.
    """
    ...


def deletePreset(nodeClassName, presetName) -> None:
    """
    Deletes a pre-created node preset
    """
    ...


def deleteUserPreset(nodeClassName, presetName) -> None:
    """
    Deletes a pre-created user node preset
    """
    ...


def deleteView(s) -> None:
    """
    Deprecated.
    """
    ...


def dependencies(nodes, what=7):
    """
    List all nodes referred to by the nodes argument.
    """
    ...


def dependentNodes(what=7, nodes=[], evaluateAll=True):
    """
    List all nodes referred to by the nodes argument.
    """
    ...


def display(s, node, title, width) -> None:
    """
    Creates a window showing the result of a python script.
    """
    ...


def endGroup() -> None:
    """
    Deprecated.
    """
    ...


def error(message) -> None:
    """
    Puts the message into the error console, treating it like an error.
    """
    ...


def execute(nameOrNode, start, end, incr, views, continueOnError=False) -> None:
    """
    execute(nameOrNode, frameRangeSet, views, continueOnError = False) 
          -> None.
    """
    ...


def executeBackgroundNuke(exe_path, nodes, frameRange, views, limits, continueOnError=False, flipbookToRun=..., flipbookOptions={}) -> None:
    """
    Run an instance of Nuke as a monitored sub process.
    """
    ...


def executeInMainThread(call, args=(), kwargs={}):
    """
    Execute the callable 'call' with optional arguments 'args' and named 
          arguments 'kwargs' i n Nuke's main thread and return immediately.
    """
    ...


def executeInMainThreadWithResult(call, args=(), kwargs={}):
    """
    Execute the callable 'call' with optional arguments 'args' and named 
          arguments 'kwargs' in Nuke's main thread and wait for the result to 
          become available.
    """
    ...


def executeMultiple(nodes, ranges, views, continueOnError=False) -> None:
    """
    Execute the current script for a specified frame range.
    """
    ...


def executing() -> bool:
    """
    Returns whether an Executable Node is currently active or not.
    """
    ...


def exists(s) -> bool:
    """
    Check for the existence of a named item.
    """
    ...


def expandSelectedGroup() -> None:
    """
    Moves all nodes from the currently selected group node into its 
          parent group, maintaining node input and output connections, and 
          deletes the group.
    """
    ...


def expr(s) -> float:
    """
    Parse a Nuke expression.
    """
    ...


def expression(s) -> float:
    """
    Parse a Nuke expression.
    """
    ...


def extractSelected() -> None:
    """
    Disconnects the selected nodes in the group from the tree, and shifts
          them to the side.
    """
    ...


def filename(node, i) -> str:
    """
    Return the filename(s) this node or group is working with.
    """
    ...


def filenameFilter(filename):
    ...


def forceClone() -> bool:
    """
    Returns:
          True if succeeded, False otherwise.
    """
    ...


def forceLoad(n) -> None:
    """
    Force the plugin to be fully instantiated.
    """
    ...


def fork():
    """
    Forks a new instance of Nuke optionally with the contents of the 
          named file.
    """
    ...


def formats() -> list:
    """
    Returns:
          List of all available formats.
    """
    ...


def frame(f) -> int:
    """
    Return or set the current frame number.
    """
    ...


def fromNode(n) -> six.binary_type:
    """
    Return the Node n as a string.
    """
    ...


def getAllUserPresets() -> None:
    """
    gets a list of all current user presets
    """
    ...


@overload
def getClipname(prompt, pattern=None, default=None, multiple: Literal[False] = False) -> six.binary_type:
    ...


@overload
def getClipname(prompt, pattern=None, default=None, multiple: Literal[True] = ...) -> List[six.binary_type]:
    """
    Pops up a file chooser dialog box.
    """
    ...


def getColor(initial) -> int:
    """
    Show a color chooser dialog and return the selected color as an int.
    """
    ...


def getColorspaceList(colorspaceKnob):
    """
    Get a list of all colorspaces listed in an enumeration knob.
    """
    ...


def getDeletedPresets() -> None:
    """
    gets a list of all currently deleted presets
    """
    ...


def getFileNameList(dir, splitSequences=False, extraInformation=False, returnDirs=True, returnHidden=False) -> str:
    """
    @param dir the directory to get sequences from @param splitSequences 
          whether to split sequences or not @param extraInformation whether or 
          not there should be extra sequence information on the sequence name 
          @param returnDirs whether to return a list of directories as well as 
          sequences @param returnHidden whether to return hidden files and 
          directories.
    """
    ...


@overload
def getFilename(message, pattern=None, default=None, favorites=None, type=None, multiple:Literal[False]=False) -> six.binary_type:
    ...
@overload
def getFilename(message, pattern=None, default=None, favorites=None, type=None, multiple:Literal[True]=...) -> List[six.binary_type]:
    """
    Pops up a file chooser dialog box.
    """
    ...


def getFonts() -> List[six.binary_type]:
    """
    Return a list of all available font families and styles
    """
    ...


def getFramesAndViews(label, default=None, maxviews=0) -> Tuple[Any, Any]:
    """
    Pops up a dialog with fields for a frame range and view selection.
    """
    ...


def getInput(prompt, default) -> str:
    """
    Pops up a dialog box with a text field for an arbitrary string.
    """
    ...


def getNodeClassName() -> None:
    """
    gets the class name for the currently selected node
    """
    ...


def getNodePresetExcludePaths() -> List[six.binary_type]:
    """
    Gets a list of all paths that are excluded from the search for node 
          presets.
    """
    ...


def getNodePresetID() -> None:
    """
    gets the node preset identifier for the currently selected node
    """
    ...


def getOcioColorSpaces() -> List[six.binary_type]:
    """
    Returns:
          list of strings
    """
    ...


def getPaneFor(panelName) -> Dock:
    """
    Returns the first pane that contains the named panel or None if it 
          can't be found.
    """
    ...


def getPresetKnobValues() -> None:
    """
    gets a list of knob values for a given preset
    """
    ...


def getPresets() -> None:
    """
    gets a list of all presets for the currently selected node's class
    """
    ...


def getPresetsMenu(Node) -> Optional[Menu]:
    """
    Gets the presets menu for the currently selected node.
    """
    ...


def getReadFileKnob(node) -> Optional[Knob]:
    """
    Gets the read knob for a node (if it exists).
    """
    ...


def getRenderProgress() -> int:
    """
    Returns:
          The progress of the render.
    """
    ...


def getToolsetExcludePaths() -> List[six.binary_type]:
    """
    Gets a list of all paths that are excluded from the search for node 
          presets.
    """
    ...


def getUserPresetKnobValues() -> None:
    """
    gets a list of knob values for a given preset
    """
    ...


def getUserPresets(Node) -> None:
    """
    gets a list of all user presets for the currently selected node's 
          class
    """
    ...


def hotkeys() -> str:
    """
    Returns the Nuke key assignments as a string formatted for use in 
          nuke.display().
    """
    ...


def import_module(name, filterRule):
    ...


def inputs(n, i) -> int:
    """
    Deprecated.
    """
    ...


def invertSelection() -> None:
    """
    Selects all unselected nodes, and deselects all selected ones.
    """
    ...


def knob(name, value, getType, getClass) -> None:
    """
    Returns or sets the entire state of a knob.
    """
    ...


def knobChanged():
    ...


def knobDefault(classknob, value) -> str:
    """
    Set a default value for knobs in nodes that belong to the same class.
    """
    ...


def knobTooltip(classknob, value) -> None:
    """
    Set an override for a tooltip on a knob.
    """
    ...


def layers(node=None) -> List[six.binary_type]:
    """
    Lists the layers in a node.
    """
    ...


def licenseInfo() -> None:
    """
    Shows information about licenses used by nuke
    """
    ...


def load(s) -> None:
    """
    Load a plugin.
    """
    ...


def loadToolset(filename=None, overwrite=-1) -> None:
    """
    Loads the tool preset with the given file name.
    """
    ...


def localisationEnabled(knob) -> bool:
    """
    Checks if localisation is enabled on a given Read_File_Knob.
    """
    ...



def makeGroup(show=True) -> Group:
    """
    Creates a new group containing copies of all the currently selected 
          nodes.
    """
    ...


def maxPerformanceInfo():
    """
    maxPerformanceInfo -> Get the max performance info for this 
          session.
    """
    ...


def memory(cmd, value) -> str or int:
    """
    Get or set information about memory usage.
    """
    ...


def menu(name) -> Menu:
    """
    Find and return the Menu object with the given name.
    """
    ...


def message(prompt) -> None:
    """
    Show an info dialog box.
    """
    ...



def nodeCopy(s) -> bool:
    """
    Copy all selected nodes into a file or the clipboard.
    """
    ...


def nodeDelete(s) -> bool:
    """
    Removes all selected nodes from the DAG.
    Returns:
        True if any nodes were deleted, False otherwise
    """
    ...


def nodePaste(s) -> Node:
    """
    Paste nodes from a script file or the clipboard.
    """
    ...


def nodesSelected() -> None:
    """
    returns true if any nodes are currently selected
    """
    ...


def numvalue(knob, default=...) -> float:
    """
    The numvalue function returns the current value of a knob.
    default to infinity
    """
    ...


def oculaPresent() -> bool:
    """
    Check whether Ocula is present.
    """
    ...


def ofxAddPluginAliasExclusion(fullOfxEffectName) -> None:
    """
    Adds the ofx effect name to a list of exclusions that will not get 
          tcl aliases automatically created for them.
    """
    ...


def ofxMenu() -> bool:
    """
    Find all the OFX plugins (by searching all the directories below 
          $OFX_PLUGIN_PATH, or by reading a cache file stored in 
          $NUKE_TEMP_DIR), then add a menu item for each of them to the main 
          menu.
    """
    ...


def ofxPluginPath(nuke) -> List[six.binary_type]:
    """
    List of all the directories Nuke searched for OFX plugins in.
    """
    ...


def ofxRemovePluginAliasExclusion(fullOfxEffectName) -> None:
    """
    Remove an ofx plugin alias exclusion that was previously added with .
    """
    ...


def onCreate():
    ...


def onDestroy():
    ...


def onScriptClose():
    ...


def onScriptLoad():
    ...


def onScriptSave():
    ...


def onUserCreate():
    ...


def openPanels() -> List:
    """
    returns a list of Nodes which have panels open.The last item in the 
          list is the currently active Node panel.
    """
    ...


def pan() -> Tuple[int, int]:
    """
    Return the pan values of a group's display.
    """
    ...


def performanceProfileFilename() -> Optional[six.binary_type]:
    """
    Returns the profile filename if performance timers are in use, 
          otherwise returns None.
    """
    ...


def pluginAddPath(args, addToSysPath=True):
    """
    Adds all the paths to the beginning of the Nuke plugin path.
    """
    ...


def pluginAppendPath(args, addToSysPath=True):
    """
    Add a filepath to the end of the Nuke plugin path.
    """
    ...


def pluginExists(name) -> bool:
    """
    This function is the same as load(), but only checks for the 
          existence of a plugin rather than loading it.
    """
    ...


def pluginInstallLocation() -> List[six.binary_type]:
    """
    The system-specific locations that Nuke will look in for third-party 
          plugins.
    """
    ...


def pluginPath() -> List[six.binary_type]:
    """
    List all the directories Nuke will search in for plugins.
    """
    ...


def plugins(switches=0, *pattern) -> List[six.binary_type]:
    """
    Returns a list of every loaded plugin or every plugin available.
    """
    ...


def recentFile(index) -> str:
    """
    Returns a filename from the recent-files list.
    """
    ...


def redo() -> None:
    """
    Perform the most recent redo.
    """
    ...


def removeAfterBackgroundFrameRender(call, args=(), kwargs={}):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeAfterBackgroundRender(call, args=(), kwargs={}):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeAfterFrameRender(call, args=(), kwargs={}, nodeClass='Write'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeAfterRecording(call, args=(), kwargs={}, nodeClass='Viewer'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeAfterRender(call, args=(), kwargs={}, nodeClass='Write'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeAfterReplay(call, args=(), kwargs={}, nodeClass='Viewer'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeAutoSaveDeleteFilter(filter):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeAutoSaveFilter(filter):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeAutoSaveRestoreFilter(filter):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeAutolabel(call, args=(), kwargs={}, nodeClass='*'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeBeforeBackgroundRender(call, args=(), kwargs={}):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeBeforeFrameRender(call, args=(), kwargs={}, nodeClass='Write'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeBeforeRecording(call, args=(), kwargs={}, nodeClass='Viewer'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeBeforeRender(call, args=(), kwargs={}, nodeClass='Write'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeBeforeReplay(call, args=(), kwargs={}, nodeClass='Viewer'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeDefaultColorspaceMapper(call, args=(), kwargs={}, nodeClass='*'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeFavoriteDir(name, type) -> None:
    """
    Remove a directory path from the favorites list.
    """
    ...


def removeFilenameFilter(call, args=(), kwargs={}, nodeClass='*'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeFilenameValidate(call, args=(), kwargs={}, nodeClass='Write'):
    """
    Remove a previously-added callback.
    """
    ...


def removeKnobChanged(call, args=(), kwargs={}, nodeClass='*', node=None):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeOnCreate(call, args=(), kwargs={}, nodeClass='*'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeOnDestroy(call, args=(), kwargs={}, nodeClass='*'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeOnScriptClose(call, args=(), kwargs={}, nodeClass='Root'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeOnScriptLoad(call, args=(), kwargs={}, nodeClass='Root'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeOnScriptSave(call, args=(), kwargs={}, nodeClass='Root'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeOnUserCreate(call, args=(), kwargs={}, nodeClass='*'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeRenderProgress(call, args=(), kwargs={}, nodeClass='Write'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def removeUpdateUI(call, args=(), kwargs={}, nodeClass='*'):
    """
    Remove a previously-added callback with the same arguments.
    """
    ...


def render(nameOrNode, start, end, incr, views, continueOnError=False) -> None:
    """
    execute(nameOrNode, frameRangeSet, views, continueOnError = False) 
          -> None.
    """
    ...


def renderProgress():
    ...


def rescanFontFolders() -> None:
    """
    Rebuild the font cache scanning all available font directories.
    """
    ...


def resetPerformanceTimers() -> None:
    """
    Clears the accumulated time on the performance timers.
    """
    ...


def restoreWindowLayout(i) -> None:
    """
    Restores a saved window layout.
    """
    ...


def resumePathProcessing() -> None:
    """
    Resume path processing.
    """
    ...


def root() -> Node:
    """
    Get the DAG's root node.
    """
    ...


def runIn(object, cmd) -> bool:
    """
    Execute commands with a given node/knob/field as the 'context'.
    """
    ...


def sample(n, c, x, y, dx, dy) -> float:
    """
    Get pixel values from an image.
    """
    ...


def saveEventGraphTimers() -> None:
    """
    Save events in the event graph.
    """
    ...


def saveToScript(filename, fileContent) -> None:
    """
    Saves the fileContent with the given filename.
    """
    ...


def saveUserPreset(node, presetName) -> None:
    """
    Saves a node's current knob values as a user preset.
    """
    ...


def saveWindowLayout(i=-1) -> None:
    """
    Saves the current window layout.
    """
    ...


def scriptClear():
    """
    Clears a Nuke script and resets all the root knobs to user defined 
          knob defaults.
    """
    ...


def scriptClose():
    """
    Close the current script or group.
    """
    ...


def scriptExit():
    """
    Exit Nuke.
    """
    ...


def scriptName() -> six.binary_type:
    """
    Return the current script's file name
    """
    ...


def scriptNew():
    """
    Start a new script.
    """
    ...


def scriptOpen():
    """
    Opens a new script containing the contents of the named file.
    """
    ...


def scriptReadFile():
    """
    Read nodes from a file.
    """
    ...


def scriptReadText():
    """
    Read nodes from a string.
    """
    ...


def scriptSave(filename=None) -> bool:
    """
    Saves the current script to the current file name.
    """
    ...


def scriptSaveAndClear(filename=None, ignoreUnsavedChanges=False) -> None:
    """
    Calls nuke.scriptSave and nuke.scriptClear
    """
    ...


def scriptSaveAs(filename=None, overwrite=-1) -> None:
    """
    Saves the current script with the given file name if supplied, or (in
          GUI mode) asks the user for one using the file chooser.
    """
    ...


def scriptSource():
    """
    Same as scriptReadFile().
    """
    ...


def script_directory():
    ...


def selectAll() -> None:
    """
    Select all nodes in the DAG.
    """
    ...


def selectConnectedNodes():
    """
    Selects all nodes in the tree of the selected node.
    """
    ...


def selectPattern() -> None:
    """
    Selects nodes according to a regular expression matching pattern, 
          entered through an input dialog.
    """
    ...


def selectSimilar(matchType) -> None:
    """
    Selects nodes that match a node in the current selection based on 
          matchType criteria.
    """
    ...


def selectedNode() -> Node:
    """
    Returns the 'node the user is thinking about'.
    """
    ...


def selectedNodes(filter) -> List:
    """
    Returns a list of all selected nodes in the current group.
    """
    ...


def setPreset(nodeClassName, presetName, knobValues) -> None:
    """
    Create a node preset for the given node using the supplied knob 
          values
    """
    ...


def setReadOnlyPresets(readOnly) -> None:
    """
    Sets whether newly created presets should be added in read-only mode.
    """
    ...


def setUserPreset(nodeClassName, presetName, knobValues) -> None:
    """
    Create a node preset for the given node using the supplied knob 
          values
    """
    ...


def show(n, forceFloat) -> None:
    """
    Opens a window for each named node, as though the user double-clicked
          on them.
    """
    ...


def showBookmarkChooser(n) -> None:
    """
    Show bookmark chooser search box.
    """
    ...


def showCreateViewsDialog(views) -> None:
    """
    Show a dialog to prompt the user to add or create missing views.
    """
    ...


def showDag(n) -> None:
    """
    Show the tree view of a group node or opens a node control panel.
    """
    ...


def showInfo(n) -> str:
    """
    Returns a long string of debugging information about each node and 
          the operators it is currently managing.
    """
    ...


def showSettings() -> None:
    """
    Show the settings of the current group.
    """
    ...


def splayNodes() -> None:
    """
    Deprecated.
    """
    ...


def startEventGraphTimers() -> None:
    """
    Start keeping track of events in the event graph.
    """
    ...


def startPerformanceTimers() -> None:
    """
    Start keeping track of accumulated time on the performance timers, 
          and display the accumulated time in the DAG.
    """
    ...


def stopEventGraphTimers() -> None:
    """
    Stop keeping track of events in the event graph.
    """
    ...


def stopPerformanceTimers() -> None:
    """
    Stop keeping track of accumulated time on the performance timers, and
          cease displaying the accumulated time in the DAG.
    """
    ...


def stripFrameRange(clipname) -> six.binary_type:
    """
    Strip out the frame range from a clipname, leaving a file path (still
          possibly with variables).
    """
    ...


def suspendPathProcessing() -> None:
    """
    Suspend path processing.
    """
    ...


def tabClose():
    """
    Close the active dock tab.
    """
    ...


def tabNext():
    """
    Make the next tab in this dock active.
    """
    ...


def tcl(s, *args) -> str:
    """
    Run a tcl command.
    """
    ...


def thisClass() -> None:
    """
    Get the class name of the current node.
    """
    ...


def thisGroup() -> Group:
    """
    Returns the current context Group node.
    """
    ...


def thisKnob() -> Knob:
    """
    Returns the current context knob if any.
    """
    ...


def thisNode() -> Node:
    """
    Return the current context node.
    """
    ...


def thisPane() -> Pane:
    """
    Returns the active pane.
    """
    ...


def thisParent() -> Node:
    """
    Returns the current context Node parent.
    """
    ...


def thisView() -> str:
    """
    Get the name of the current view.
    """
    ...


def toNode(s) -> Node:
    """
    Search for a node in the DAG by name and return it as a Python 
          object.
    """
    ...


def toggleFullscreen() -> None:
    """
    Toggles between windowed and fullscreen mode.
    """
    ...


def toggleViewers() -> None:
    """
    Toggles all the viewers on and off.
    """
    ...


def toolbar(name, create=True) -> ToolBar:
    """
    Find and return the ToolBar object with the given name.
    """
    ...


def tprint(value, sep=' ', end='\n', file=...) -> None:
    """
    Prints the values to a stream, or to stdout by default.
    """
    ...


def undo() -> None:
    """
    Perform the most recent undo.
    """
    ...


def updateUI():
    ...


def usingOcio() -> bool:
    """
    returns true if using OCIO instead of Nuke LUTs
    """
    ...


def usingPerformanceTimers() -> bool:
    """
    Return true if performance timers are in use.
    """
    ...


def validateFilename(filename):
    ...


def value(knob, default) -> six.binary_type:
    """
    The value function returns the current value of a knob.
    """
    ...


def views() -> List:
    """
    List of all the globally existing views.
    """
    ...


def waitForThreadsToFinish() -> str:
    """
    Returns true if Nuke should wait for any Python threads to finish 
          before exitting.
    """
    ...


def warning(message) -> None:
    """
    Puts the message into the error console, treating it like a warning.
    """
    ...


def zoom(scale, center, group) -> float:
    """
    Change the zoom and pan of a group's display.
    """
    ...


def zoomToFitSelected() -> None:
    """
    Does a zoom to fit on the selected nodes in the DAG
    """
    ...
