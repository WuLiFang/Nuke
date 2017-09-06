# -*- coding=UTF-8 -*-
"""Upload files to server.  """

import os
import sys
import re

from wlf.Qt import QtCore, QtWidgets, QtCompat, QtGui
from wlf.Qt.QtWidgets import QDialog, QApplication, QFileDialog
from wlf.files import version_filter, copy, remove_version,\
    is_same, get_unicode, get_server, url_open
from wlf.progress import Progress, CancelledError, HAS_NUKE
import wlf.config

__version__ = '0.5.0'


class Config(wlf.config.Config):
    """A disk config can be manipulated like a dict."""

    default = {
        'DIR': 'N:/',
        'SERVER': 'Z:\\',
        'PROJECT': 'SNJYW',
        'FOLDER': 'Comp\\mov',
        'EPISODE': '',
        'SCENE': '',
    }
    path = os.path.expanduser('~/.wlf.uploader.json')


class Dialog(QDialog):
    """Main GUI dialog.  """

    def __init__(self, parent=None):
        self._ignore = []

        def _icon():
            _stdicon = self.style().standardIcon

            _icon = _stdicon(QtWidgets.QStyle.SP_FileDialogListView)
            self.syncButton.setIcon(_icon)

            _icon = _stdicon(QtWidgets.QStyle.SP_DirOpenIcon)
            self.toolButtonOpenDir.setIcon(_icon)
            self.toolButtonOpenServer.setIcon(_icon)

            _icon = _stdicon(QtWidgets.QStyle.SP_DialogOpenButton)
            self.dirButton.setIcon(_icon)
            self.serverButton.setIcon(_icon)

            _icon = _stdicon(QtWidgets.QStyle.SP_FileDialogToParent)
            self.setWindowIcon(_icon)

        def _actions():
            self.actionDir.triggered.connect(self.ask_dir)
            self.actionSync.triggered.connect(self.upload)
            self.actionServer.triggered.connect(self.ask_server)
            self.actionUpdateUI.triggered.connect(self.update_ui)
            self.actionOpenDir.triggered.connect(self.open_dir)
            self.actionOpenServer.triggered.connect(self.open_server)

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
                elif isinstance(edit, QtWidgets.QToolBox):
                    edit.currentChanged.connect(
                        lambda index, ex=edit, k=key: _set_config(
                            k,
                            index
                        )
                    )
                    edit.currentChanged.connect(self.update_ui)
                else:
                    print(u'待处理的控件: {} {}'.format(type(edit), edit))

            self.dirEdit.editingFinished.connect(self.autoset)
            self.listWidget.itemDoubleClicked.connect(lambda item: url_open(
                os.path.join(self.dir, item.text()), isfile=True))

        def _recover():
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
                    elif isinstance(qt_edit, QtWidgets.QToolBox):
                        qt_edit.setCurrentIndex(self._config[k])
                except KeyError as ex:
                    print(ex)
            if HAS_NUKE:
                from node import Last
                if Last.mov_path:
                    self.dir = get_unicode(Last.mov_path)
            self.autoset()

        QDialog.__init__(self, parent)
        QtCompat.loadUi(os.path.join(__file__, '../uploader.ui'), self)

        self.edits_key = {
            self.serverEdit: 'SERVER',
            self.folderEdit: 'FOLDER',
            self.dirEdit: 'DIR',
            self.projectEdit: 'PROJECT',
            self.epEdit: 'EPISODE',
            self.scEdit: 'SCENE',
            self.toolBox: 'MODE',
        }
        self._config = Config()
        self.version_label.setText('v{}'.format(__version__))
        self._start_update()

        _icon()
        _actions()
        _edits()
        _recover()
        self._brushes = {}
        if HAS_NUKE:
            self._brushes['files'] = QtGui.QBrush(QtGui.QColor(200, 200, 200))
            self._brushes['ignore'] = QtGui.QBrush(QtGui.QColor(100, 100, 100))
        else:
            self._brushes['files'] = QtGui.QBrush(QtCore.Qt.black)
            self._brushes['ignore'] = QtGui.QBrush(QtCore.Qt.gray)

    def _start_update(self):
        """Start a thread for update."""

        self.update_ui()
        _timer = QtCore.QTimer(self)
        _timer.timeout.connect(self.update_ui)
        _timer.start(1000)

    def update_ui(self):
        """Update dialog UI content.  """
        files = self.files()
        mode = self.mode()

        def _button_enabled():
            if os.path.exists(get_server(self.server))\
                    and os.path.isdir(os.path.dirname(self.dest)) and files:
                self.syncButton.setEnabled(True)
            else:
                self.syncButton.setEnabled(False)

        def _list_widget():
            widget = self.listWidget
            all_files = files + self._ignore

            for i in xrange(widget.count()):
                item = widget.item(i)
                if item.text() not in all_files:
                    widget.takeItem(widget.indexFromItem(item))

            for i in all_files:
                try:
                    item = self.listWidget.findItems(
                        i, QtCore.Qt.MatchExactly)[0]
                except IndexError:
                    item = QtWidgets.QListWidgetItem(i, widget)
                    item.setCheckState(QtCore.Qt.Checked)
                if i in files:
                    item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                                  QtCore.Qt.ItemIsEnabled)
                    item.setForeground(self._brushes['files'])
                else:
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    item.setForeground(self._brushes['ignore'])
                    item.setCheckState(QtCore.Qt.Unchecked)

            widget.sortItems()

        _button_enabled()
        _list_widget()
        if mode == 0:
            self.syncButton.setText(u'上传至: {}'.format(self.dest))
        elif mode == 1:
            self.syncButton.setText(u'上传至CGTeamWork')
            self.syncButton.setEnabled(False)

    def files(self):
        """Return files in folder as list.  """

        self._ignore = []
        if not os.path.isdir(self.dir):
            return []
        ret = version_filter(i for i in os.listdir(self.dir)
                             if i.endswith('.mov'))

        for i in list(ret):
            src = os.path.join(self.dir, i)
            dst = os.path.join(self.dest, remove_version(i))
            if is_same(src, dst):
                ret.remove(i)
                self._ignore.append(i)

        return ret

    def checked_files(self):
        """Return files checked in listwidget.  """
        widget = self.listWidget
        return list(widget.item(i).text() for i in xrange(widget.count())
                    if widget.item(i).checkState())

    def upload(self):
        """Upload videos to server.  """
        if not os.path.exists(self.dest):
            os.mkdir(self.dest)
        try:
            task = Progress()
            files = self.checked_files()
            all_num = len(files)
            for index, i in enumerate(files):
                task.set(index * 100 // all_num, i)
                src = os.path.join(self.dir, i)
                dst = os.path.join(self.dest, remove_version(i))
                copy(src, dst)
        except CancelledError:
            pass

        self.activateWindow()

    @property
    def dest(self):
        """File upload destination.  """
        ret = os.path.join(
            self.server,
            self.project,
            self.folderEdit.text(),
            self.epEdit.text(),
            self.scEdit.text()
        )
        ret = os.path.normpath(ret)
        return ret

    def mode(self):
        """Upload mode. """
        return self.toolBox.currentIndex()

    @property
    def dir(self):
        """Current working dir.  """
        return self.dirEdit.text()

    @dir.setter
    def dir(self, value):
        self.dirEdit.setText(os.path.normpath(value))

    @property
    def server(self):
        """Current server path.  """
        return self.serverEdit.text()

    @property
    def project(self):
        """Current working dir.  """
        return self.projectEdit.text()

    def ask_dir(self):
        """Show a dialog ask user self._config['DIR'].  """

        file_dialog = QFileDialog()
        _dir = file_dialog.getExistingDirectory(
            dir=os.path.dirname(self._config['DIR'])
        )
        if _dir:
            self.dir = _dir
            self._config['DIR'] = _dir
        self.autoset()

    def autoset(self):
        """Auto set fields by dir.  """

        self.dir = self.dir
        pat = re.compile(r'.*\\(ep.*?)\\.*\\(\d+[a-z]*)\\.*', flags=re.I)
        match = pat.match(self.dir)
        if match:
            self.epEdit.setText(match.groups()[0])
            self.scEdit.setText(match.groups()[1])

    def ask_server(self):
        """Show a dialog ask user config['SERVER'].  """

        file_dialog = QFileDialog()
        dir_ = file_dialog.getExistingDirectory(
            dir_=os.path.dirname(self._config['SERVER'])
        )
        if dir_:
            self.serverEdit.setText(dir_)

    def open_dir(self):
        """Open config['DIR'] in explorer.  """

        url_open('file://{}'.format(self._config['DIR']))

    def open_server(self):
        """Open config['SERVER'] in explorer.  """

        url_open('file://{}'.format(self._config['SERVER']))


def main():
    """Run this script standalone.  """

    app = QApplication(sys.argv)
    frame = Dialog()
    frame.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
