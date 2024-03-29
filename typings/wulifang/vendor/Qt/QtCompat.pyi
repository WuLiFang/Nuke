# -*- coding=UTF-8 -*-
# This typing file was generated by typing_from_help.py
"""
QtCompat
"""
from typing import Any
from wulifang._compat.str import Str

class QFileDialog(QtCompat):
    getOpenFileName: ...
    """
    <built-in function getOpenFileName>
    """

    getOpenFileNames: ...
    """
    <built-in function getOpenFileNames>
    """

    getSaveFileName: ...
    """
    <built-in function getSaveFileName>
    """

    ...

class QHeaderView(QtCompat):
    def sectionResizeMode(self, *args, **kwargs):
        """ """
        ...
    def sectionsClickable(self, *args, **kwargs):
        """ """
        ...
    def sectionsMovable(self, *args, **kwargs):
        """ """
        ...
    def setSectionResizeMode(self, *args, **kwargs):
        """ """
        ...
    def setSectionsClickable(self, *args, **kwargs):
        """ """
        ...
    def setSectionsMovable(self, *args, **kwargs):
        """ """
        ...
    ...

def _cli(args):
    """
    Qt.py command-line interface
    """
    ...

def _convert(lines):
    """
    Convert compiled .ui file from PySide2 to Qt.py

    Arguments:
        lines (list): Each line of of .ui file

    Usage:
        >> with open("myui.py") as f:
        ..   lines = _convert(f.readlines())
    """
    ...

def _loadUi(path: str, /) -> Any: ...

loadUi = _loadUi

load_ui = _loadUi

qInstallMessageHandler = _qInstallMessageHandler

setSectionResizeMode = setResizeMode

__all__: ...
"""
['QFileDialog', 'QHeaderView', '__doc__', '__name__', '_cli'...
"""
