# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=none

from __future__ import absolute_import, division, print_function, unicode_literals


import glob
import os
import re
import json
import sys
import codecs
import webbrowser
import tempfile
import io

from wulifang.vendor.Qt import QtCompat, QtCore, QtWidgets
from wulifang.vendor.Qt.QtWidgets import QFileDialog


from wulifang._util import (
    JSONStorageItem,
    force_rename,
    cast_str,
    cast_text,
    assert_isinstance,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import (
        Optional,
    )


_GLOB_PATTERNS = JSONStorageItem(
    "globPatterns@232186ac-c8f9-46b2-994f-dc43fdc4bdd8", lambda: "E:/example/*"
)


_RE_PATTERNS = JSONStorageItem(
    "rePatterns@232186ac-c8f9-46b2-994f-dc43fdc4bdd8", lambda: ""
)
_VERSION = "v2.0.0"


def _migrate_legacy_config():
    p = os.path.expanduser("~/.wlf.scanner.json")
    if os.path.exists(p):
        with codecs.open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "patterns" in data:
                _GLOB_PATTERNS.set(data["patterns"])
            if "regex_pattern" in data:
                _RE_PATTERNS.set(data["regex_pattern"])
        force_rename(p, p + "~")


def _connect_json_storage(_edit, _item):
    # type: (QtWidgets.QWidget, JSONStorageItem[str]) -> None
    if isinstance(_edit, QtWidgets.QTextEdit):
        e = assert_isinstance(_edit, QtWidgets.QTextEdit)
        e.setText(cast_str(_item.get()))
        e.textChanged.connect(lambda: _item.set(cast_text(e.toPlainText())))
    elif isinstance(_edit, QtWidgets.QLineEdit):
        e = assert_isinstance(_edit, QtWidgets.QLineEdit)
        e.setText(cast_str(_item.get()))
        e.editingFinished.connect(lambda: _item.set(cast_text(e.text())))


class MainWindow(QtWidgets.QMainWindow):
    """Main dialog."""

    def __init__(self, parent=None):
        # type: (Optional[QtWidgets.QWidget]) -> None

        super(MainWindow, self).__init__(parent)
        self._ui = QtCompat.loadUi(os.path.join(__file__, "../_find_empty_dir.ui"))
        self.setCentralWidget(self._ui)

        _migrate_legacy_config()
        _connect_json_storage(self._glob_pattern_edit(), _GLOB_PATTERNS)
        _connect_json_storage(self._re_pattern_edit(), _RE_PATTERNS)

        self._glob_pattern_edit().textChanged.connect(
            self.reset_status_bar,
        )
        self._re_pattern_edit().editingFinished.connect(
            self.reset_status_bar,
        )
        self._ui.toolButtonPath.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_DialogOpenButton)
        )
        self._ui.setWindowIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogToParent)
        )
        self._ui.actionAskPath.triggered.connect(self.ask_path)
        self._ui.actionTxt.triggered.connect(self.generate_txt)
        self._ui.actionRefresh.triggered.connect(self.update_ui)
        self._ui.labelVersion.setText(_VERSION)
        self.setWindowTitle(cast_str("查找空文件夹"))
        self.resize(500, 600)
        self._result = []
        self.reset_status_bar()

    def reset_status_bar(self):
        self.statusBar().showMessage(cast_str("点击刷新按钮更新结果"))

    def _glob_pattern_edit(self):
        # type: () -> QtWidgets.QTextEdit
        return self._ui.textEditPatterns

    def _re_pattern_edit(self):
        # type: () -> QtWidgets.QLineEdit
        return self._ui.lineEditRegexPattern

    def ask_path(self):
        """Show a dialog ask user self._config['DIR']."""

        p = QFileDialog.getExistingDirectory(self, dir="/")
        if p:
            _GLOB_PATTERNS.set((_GLOB_PATTERNS.get() + "\n%s/*" % p).strip("\n"))
            self._glob_pattern_edit().setText(cast_str(_GLOB_PATTERNS.get()))

    def result(self):
        # type: () -> list[str]
        """match result."""
        ret = set()  # type: set[str]

        re_pattern = _RE_PATTERNS.get()
        for pattern in _GLOB_PATTERNS.get().splitlines():
            if not pattern:
                continue
            self.statusBar().showMessage(cast_str(pattern))
            for i in glob.glob(pattern):
                QtCore.QCoreApplication.processEvents()
                self.statusBar().showMessage(cast_str(i))
                if not os.path.isdir(i):
                    continue
                if re_pattern and not re.match(re_pattern, i):
                    continue
                if os.listdir(i):
                    continue
                ret.add(i)
        self.statusBar().showMessage(cast_str("扫描完毕"))

        return sorted(ret)

    def update_ui(self):
        """Update dialog UI content."""

        self._result = self.result()
        self._ui.listView.setModel(QtCore.QStringListModel(self._result))

    def generate_txt(self):
        """Generate txt."""
        fd, name = tempfile.mkstemp(".txt", "empty-dirs-")
        with io.open(fd, "w", encoding="utf-8") as f:
            f.write("\n".join(self._result))
        webbrowser.open(name)


def dialog():
    nuke_window = QtWidgets.QApplication.activeWindow()
    frame = MainWindow(nuke_window)
    geo = frame.geometry()
    geo.moveCenter(nuke_window.geometry().center())
    frame.setGeometry(geo)
    frame.show()


def main():
    app = QtWidgets.QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
