# -*- coding=UTF-8 -*-
"""Found empty shot forlder.  """

from __future__ import absolute_import

import glob
import os
import re
import sys
import webbrowser

from Qt import QtCompat, QtCore, QtWidgets
from Qt.QtWidgets import QFileDialog

import __version__
import wlf.config


class Config(wlf.config.Config):
    """A disk config can be manipulated like a dict."""

    default = {
        "patterns": "E:/example/*",
        "regex_pattern": "",
    }
    path = os.path.expanduser("~/.wlf.scanner.json")


class MainWindow(QtWidgets.QMainWindow):
    """Main dialog."""

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
                if isinstance(edit, QtWidgets.QTextEdit):
                    edit.textChanged.connect(
                        lambda e=edit, k=key: _set_config(k, e.toPlainText())
                    )
                if isinstance(edit, QtWidgets.QLineEdit):
                    edit.editingFinished.connect(
                        lambda e=edit, k=key: _set_config(k, e.text())
                    )
                elif isinstance(edit, QtWidgets.QCheckBox):
                    edit.stateChanged.connect(
                        lambda state, k=key: _set_config(k, state)
                    )
                elif isinstance(edit, QtWidgets.QComboBox):
                    edit.currentIndexChanged.connect(
                        lambda index, ex=edit, k=key: _set_config(k, ex.itemText(index))
                    )

            for qt_edit, k in self.edits_key.items():
                if isinstance(qt_edit, QtWidgets.QLineEdit):
                    qt_edit.setText(self._config[k])
                if isinstance(qt_edit, QtWidgets.QTextEdit):
                    qt_edit.setText(self._config[k])
                elif isinstance(qt_edit, QtWidgets.QCheckBox):
                    qt_edit.setCheckState(QtCore.Qt.CheckState(self._config[k]))
                elif isinstance(qt_edit, QtWidgets.QComboBox):
                    qt_edit.setCurrentIndex(qt_edit.findText(self._config[k]))

        super(MainWindow, self).__init__(parent)
        self._ui = QtCompat.loadUi(os.path.join(__file__, "../scanner.ui"))
        self.setCentralWidget(self._ui)
        self.edits_key = {
            self.textEditPatterns: "patterns",
            self.lineEditRegexPattern: "regex_pattern",
        }

        self.textEditPatterns.textChanged.connect(
            self.reset_status_bar,
        )
        self.lineEditRegexPattern.editingFinished.connect(
            self.reset_status_bar,
        )
        self._config = Config()
        self.labelVersion.setText("v{}".format(__version__.VERSION))
        self.setWindowTitle(u"空文件夹扫描")
        self.resize(500, 600)

        _icon()
        _actions()
        _edits()
        self._result = []
        self.reset_status_bar()

    def reset_status_bar(self):
        self.statusBar().showMessage(u"点击刷新按钮更新结果".encode("utf-8"))

    def __getattr__(self, name):
        return getattr(self._ui, name)

    @property
    def patterns(self):
        """Current pattern to scan."""
        return self.textEditPatterns.toPlainText().split("\n")

    @patterns.setter
    def patterns(self, value):
        """Current pattern to scan."""
        return self.textEditPatterns.setText("\n".join(value))

    @property
    def regex_pattern(self):
        """re match pattern."""
        return self.lineEditRegexPattern.text()

    def ask_path(self):
        """Show a dialog ask user self._config['DIR']."""

        _dir = QFileDialog.getExistingDirectory(self, dir="/")
        if _dir:
            self.patterns += [_dir + "/*"]

    def result(self):
        """match result."""
        ret = set()

        for pattern in self.patterns:
            self.statusBar().showMessage(pattern)
            for i in glob.glob(pattern):
                if not os.path.isdir(i):
                    continue
                if not re.match(self.regex_pattern, i):
                    continue
                if os.listdir(i):
                    continue
                ret.add(i)
        self.statusBar().showMessage(u"扫描完毕".encode("utf-8"))

        return sorted(ret)

    def update_ui(self):
        """Update dialog UI content."""

        self._result = self.result()
        self.listView.setModel(QtCore.QStringListModel(self._result))

    def generate_txt(self):
        """Generate txt."""
        path = os.path.expanduser("~/wlf.scanner.txt")
        with open(path, "w") as f:
            _ = f.write("\n".join(self._result))
        _ = webbrowser.open(path)


def call_from_nuke():
    """Run this script standaloe."""
    nuke_window = QtWidgets.QApplication.activeWindow()
    frame = MainWindow(nuke_window)
    geo = frame.geometry()
    geo.moveCenter(nuke_window.geometry().center())
    frame.setGeometry(geo)
    frame.show()


def main():
    """Run this script standalone."""

    app = QtWidgets.QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
