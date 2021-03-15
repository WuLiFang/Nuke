"""
This type stub file was generated by pyright.
"""

import nukescripts

def getNukeUserFolder():
  ...

def buildPresetFileList(fullPath):
  ...

class CreateNodePresetsPanel(nukescripts.PythonPanel):
  def __init__(self, node) -> None:
    ...
  
  def createPreset(self):
    ...
  
  def getPresetPath(self):
    ...
  
  def knobChanged(self, knob):
    ...
  


class UserPresetsLoadPanel(nukescripts.PythonPanel):
  def __init__(self) -> None:
    ...
  
  def loadPreset(self):
    ...
  
  def knobChanged(self, knob):
    ...
  


class UserPresetsDeletePanel(nukescripts.PythonPanel):
  def __init__(self) -> None:
    ...
  
  def deletePreset(self):
    ...
  
  def knobChanged(self, knob):
    ...
  


class PresetsLoadPanel(nukescripts.PythonPanel):
  def __init__(self) -> None:
    ...
  
  def loadPreset(self):
    ...
  
  def knobChanged(self, knob):
    ...
  


class PresetsDeletePanel(nukescripts.PythonPanel):
  def __init__(self) -> None:
    ...
  
  def deletePreset(self):
    ...
  
  def knobChanged(self, knob):
    ...
  


def processPresetFile(location):
  ...

def createNodePresetsMenu():
  ...

def populatePresetsMenu(nodeName, className):
  ...

def buildUserPresetLoadPanel():
  ...

def buildPresetLoadPanel():
  ...

def buildPresetSavePanel(nodeName, node=...):
  ...

def buildUserPresetDeletePanel():
  ...

def buildPresetDeletePanel():
  ...

def getItemDirName(d, item):
  ...

def saveNodePresets():
  ...

def createNodePreset(node, name):
  ...

def deleteNodePreset(classname, presetName):
  ...

def deleteUserNodePreset(classname, presetName):
  ...
