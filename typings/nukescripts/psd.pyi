"""
This type stub file was generated by pyright.
"""

import threading
import nuke

class Layer:
    def __init__(self) -> None: ...

def getLayers(metadata): ...
def breakoutLayers(node: nuke.Node, sRGB: bool = ...) -> None: ...

class BreakoutThreadClass(threading.Thread):
    node: nuke.Node
    def __init__(self, node: nuke.Node) -> None: ...
    def run(self) -> None: ...

def doReaderBreakout(): ...
