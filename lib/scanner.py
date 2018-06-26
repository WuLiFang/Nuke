# -*- coding=UTF-8 -*-
"""Found empty shot forlder.  """

from __future__ import absolute_import

import os
import re
import sys
import webbrowser

from Qt import QtCompat, QtCore, QtWidgets
from Qt.QtWidgets import QFileDialog

import wlf.config
from __about__ import __version__


class Config(wlf.config.Config):
    """A disk config can be manipulated like a dict."""

    default = {
        'path': 'E:/test/server/SNJYW/Render',
        'shot_pattern': '',
    }
    path = os.path.expanduser('~/.wlf.scanner.json')


class MainWindow(QtWidgets.QMainWindow):
    """Main dialog.  """

    def __init__(self, parent=None):

        def _icon():
            _stdicon = self.style().standardIcon

            _icon = _stdicon(QtWidgets.QStyle.SP_DialogOpenButton)
            self._ui.toolButtonPath.setIcon(_icon)

            _icon = _stdicon(QtWidgets.QStyle.SP_FileDialogToParent)
            self._ui.setWindowIcon(_icon)

        def _actions():
            self._ui.actionAskPath.triggered.connect(self.ask_path)
            self._ui.actionTxt.triggered.connect(self.generate_txt)
            self._ui.actionRefresh.triggered.connect(self.update_ui)

        def _edits():
            def _set_config(k, v):
                self._config[k] = v

            for edit, key in self.edits_key.items():
                if isinstance(edit, QtWidgets.QLineEdit):
                    edit.editingFinished.connect(
                        lambda e=edit, k=key: _set_config(k, e.text())
                    )
                    edit.editingFinished.connect(self.update_ui)
                elif isinstance(edit, QtWidgets.QCheckBox):
                    edit.stateChanged.connect(
                        lambda state, k=key: _set_config(k, state)
                    )
                    edit.stateChanged.connect(self.update_ui)
                elif isinstance(edit, QtWidgets.QComboBox):
                    edit.currentIndexChanged.connect(
                        lambda index, ex=edit, k=key: _set_config(
                            k,
                            ex.itemText(index)
                        )
                    )
                else:
                    print(u'待处理的控件: {} {}'.format(type(edit), edit))

            for qt_edit, k in self.edits_key.items():
                try:
                    if isinstance(qt_edit, QtWidgets.QLineEdit):
                        qt_edit.setText(self._config[k])
                    elif isinstance(qt_edit, QtWidgets.QCheckBox):
                        qt_edit.setCheckState(
                            QtCore.Qt.CheckState(self._config[k])
                        )
                    elif isinstance(qt_edit, QtWidgets.QComboBox):
                        qt_edit.setCurrentIndex(
                            qt_edit.findText(self._config[k]))
                except KeyError as ex:
                    print(ex)

        super(MainWindow, self).__init__(parent)
        self._ui = QtCompat.loadUi(os.path.join(__file__, '../scanner.ui'))
        self.setCentralWidget(self._ui)
        self.edits_key = {
            self.lineEditPath: 'path',
            self.lineEditShotPattern: 'shot_pattern'
        }
        self._config = Config()
        self.labelVersion.setText('v{}'.format(__version__))
        self.setWindowTitle(u'空文件夹扫描')
        self.resize(500, 600)

        _icon()
        _actions()
        _edits()
        self._shots = []

    def showEvent(self, event):
        self.update_ui()
        event.accept()

    def __getattr__(self, name):
        return getattr(self._ui, name)

    def update_ui(self):
        """Update dialog UI content.  """

        start = len(self.path)
        self._shots = list(i[start:] for i in self.shots())
        self.listView.setModel(QtCore.QStringListModel(self._shots))

    def shots(self):
        """empty shots contained in path.  """
        ret = []
        for dirpath, dirnames, filenames in os.walk(self.path):
            QtWidgets.QApplication.processEvents()
            if re.match(self.shot_pattern, os.path.basename(dirpath)):
                if not filenames and not dirnames:
                    ret.append(dirpath)
                del dirnames[:]
            self.statusBar().showMessage(dirpath)
        self.statusBar().clearMessage()

        return sorted(ret)

    def generate_txt(self):
        """Generate txt."""
        path = os.path.expanduser('~/wlf.scanner.txt')
        with open(path, 'w') as f:
            f.write('\n'.join(self._shots))
        webbrowser.open(path)

    def ask_path(self):
        """Show a dialog ask user self._config['DIR'].  """

        default_dir = os.path.dirname(self.path)

        _dir = QFileDialog.getExistingDirectory(self, dir=default_dir)
        if _dir:
            self.path = _dir

    @property
    def path(self):
        """Current path to scan.  """
        return self.lineEditPath.text()

    @path.setter
    def path(self, value):
        """Current path to scan.  """
        return self.lineEditPath.setText(value)

    @property
    def shot_pattern(self):
        """Current shot re match pattern.  """
        return self.lineEditShotPattern.text()


def call_from_nuke():
    """Run this script standaloe.  """
    nuke_window = QtWidgets.QApplication.activeWindow()
    frame = MainWindow(nuke_window)
    geo = frame.geometry()
    geo.moveCenter(nuke_window.geometry().center())
    frame.setGeometry(geo)
    frame.show()


def main():
    """Run this script standalone.  """

    app = QtWidgets.QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
