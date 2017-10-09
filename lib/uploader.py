# -*- coding=UTF-8 -*-
"""Upload files to server.  """

import os
import sys
import threading
import time
import webbrowser

import wlf.config
from wlf import cgtwq
from wlf.decorators import run_async
from wlf.files import copy, is_same, version_filter
from wlf.notify import HAS_NUKE, CancelledError, Progress
from wlf.path import get_server, get_unicode, remove_version, split_version
from wlf.Qt import QtCompat, QtCore, QtGui, QtWidgets
from wlf.Qt.QtWidgets import QApplication, QDialog, QFileDialog

__version__ = '0.6.12'


class Config(wlf.config.Config):
    """A disk config can be manipulated like a dict."""

    default = {
        'DIR': 'N:/',
        'SERVER': 'Z:\\',
        'PROJECT': 'SNJYW',
        'FOLDER': 'Comp\\mov',
        'EPISODE': '',
        'SCENE': '',
        'MODE': 1,
        'IS_SUBMIT': 2,
        'IS_BURN_IN': 2
    }
    path = os.path.expanduser('~/.wlf.uploader.json')


class Dialog(QDialog):
    """Main GUI dialog.  """
    is_check_account = True
    _config = Config()

    def __init__(self, parent=None):
        self._uploaded_files = []

        def _icon():
            _stdicon = self.style().standardIcon

            _icon = _stdicon(QtWidgets.QStyle.SP_DirOpenIcon)
            self.toolButtonOpenDir.setIcon(_icon)
            self.toolButtonOpenServer.setIcon(_icon)

            _icon = _stdicon(QtWidgets.QStyle.SP_DialogOpenButton)
            self.dirButton.setIcon(_icon)
            self.serverButton.setIcon(_icon)

            _icon = _stdicon(QtWidgets.QStyle.SP_FileDialogToParent)
            self.syncButton.setIcon(_icon)
            self.setWindowIcon(_icon)

        def _actions():
            self.actionDir.triggered.connect(self.ask_dir)
            self.actionSync.triggered.connect(self.upload)
            self.actionServer.triggered.connect(self.ask_server)
            self.actionUpdateUI.triggered.connect(self.update_ui)
            self.actionOpenDir.triggered.connect(
                lambda: webbrowser.open(self._config['DIR']))
            self.actionOpenServer.triggered.connect(
                lambda: webbrowser.open(self._config['SERVER']))

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
                    print('wlf.uploader: not found key {} in config'.format(ex))
            if HAS_NUKE:
                from node import Last
                if Last.mov_path:
                    self.directory = get_unicode(
                        os.path.dirname(Last.mov_path))

        QDialog.__init__(self, parent)
        QtCompat.loadUi(os.path.abspath(
            os.path.join(__file__, '../uploader.ui')), self)

        self.edits_key = {
            self.serverEdit: 'SERVER',
            self.folderEdit: 'FOLDER',
            self.dirEdit: 'DIR',
            self.projectEdit: 'PROJECT',
            self.epEdit: 'EPISODE',
            self.scEdit: 'SCENE',
            self.toolBox: 'MODE',
            self.checkBoxSubmit: 'IS_SUBMIT',
            self.checkBoxBurnIn: 'IS_BURN_IN',
        }
        self._file_list_widget = FileListWidget(self.listWidget)
        self._cgtw_dests = {}
        self._lock = threading.Lock()
        self.version_label.setText('v{}'.format(__version__))

        _icon()
        _actions()
        _edits()
        _recover()

    def closeEvent(self, event):
        """override.  """
        event.accept()
        self.hideEvent(event)

    def showEvent(self, event):
        def _run():
            lock = self._lock
            while lock.acquire(False):
                self.update_ui()
                time.sleep(0.1)
                lock.release()
        self.update_ui()
        thread = threading.Thread(name='DialogUpdate', target=_run)
        thread.daemon = True
        thread.start()
        self._file_list_widget.showEvent(event)
        event.accept()

    def hideEvent(self, event):
        event.accept()
        self._lock.acquire()
        self._lock.release()
        self._file_list_widget.hideEvent(event)

    def update_ui(self):
        """Update dialog UI content.  """

        mode = self.mode()
        sync_button_enable = any(self._file_list_widget.checked_files)
        sync_button_text = u'上传至CGTeamWork'
        if mode == 0:
            sync_button_enable &= os.path.exists(get_server(self.server))\
                and os.path.isdir(os.path.dirname(self.dest_folder))
            sync_button_text = u'上传至: {}'.format(self.dest_folder)

        self.syncButton.setText(sync_button_text)
        self.syncButton.setEnabled(sync_button_enable)

    @run_async
    def upload(self):
        """Upload videos to server.  """

        try:
            files = list(self.checked_files)
            task = Progress(total=len(files))
            for i in files:
                task.step(i)
                src = os.path.join(self.directory, i)
                dst = self.get_dest(i)
                if isinstance(dst, Exception):
                    self.error(u'{}\n-> {}'.format(i, dst))
                    continue
                copy(src, dst)
                if self.is_submit and self.mode() == 1:
                    cgtwq.Shot(split_version(i)[0]).submit(
                        [dst], note='自MOV上传工具提交')

        except CancelledError:
            pass

        self.activateWindow()

    @property
    def dest_folder(self):
        """File upload folder destination.  """

        ret = os.path.join(
            self.server,
            self.project,
            self.folderEdit.text(),
            self.epEdit.text(),
            self.scEdit.text()
        )
        ret = os.path.normpath(ret)
        return ret

    def get_dest(self, filename, refresh=False):
        """Get destination for @filename. """

        mode = self.mode()
        if mode == 0:
            return os.path.join(self.dest_folder, remove_version(filename))
        elif mode == 1:
            ret = self._cgtw_dests.get(filename)
            if not ret or (isinstance(ret, Exception) and refresh):
                try:
                    shot = cgtwq.Shot(split_version(filename)[0])
                    shot.check_account()
                    ret = shot.video_dest
                except cgtwq.LoginError as ex:
                    self.error(u'需要登录CGTeamWork')
                    ret = ex
                except cgtwq.IDError as ex:
                    self.error(u'{}: CGTW上未找到对应镜头'.format(filename))
                    ret = ex
                except cgtwq.AccountError as ex:
                    self.error(u'{}\n已被分配给: {}\n当前用户: {}'.format(
                        filename, ex.owner or u'<未分配>', ex.current))
                    ret = ex
                self._cgtw_dests[filename] = ret
            return ret
        else:
            raise ValueError('No such mode. {}'.format(mode))

    def error(self, message):
        """Show error.  """
        self.textEdit.append(u'{}\n'.format(message))

    def mode(self):
        """Upload mode. """
        return self.toolBox.currentIndex()

    @property
    def directory(self):
        """Current working dir.  """
        return self.dirEdit.text()

    @directory.setter
    def directory(self, value):
        value = os.path.normpath(value)
        if value != self.directory:
            self.dirEdit.setText(value)

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
            self.directory = _dir
            self._config['DIR'] = _dir

    @property
    def is_submit(self):
        """Submit when upload or not.  """
        return self.checkBoxSubmit.checkState()

    @property
    def checked_files(self):
        """Return files checked in listwidget.  """
        return self._file_list_widget.checked_files

    def ask_server(self):
        """Show a dialog ask user config['SERVER'].  """

        file_dialog = QFileDialog()
        dir_ = file_dialog.getExistingDirectory(
            dir_=os.path.dirname(self._config['SERVER'])
        )
        if dir_:
            self.serverEdit.setText(dir_)


class FileListWidget(object):
    """Folder viewer.  """
    widget = None
    parent = None
    local_files = None
    uploaded_files = None
    burnin_folder = 'burn-in'

    def __init__(self, list_widget):
        self.widget = list_widget
        self.parent = self.widget.parent()
        assert isinstance(self.parent, Dialog)
        self.local_files = []
        self.uploaded_files = []
        self._brushes = {}
        self._lock = threading.Lock()
        if HAS_NUKE:
            self._brushes['local'] = QtGui.QBrush(QtGui.QColor(200, 200, 200))
            self._brushes['uploaded'] = QtGui.QBrush(
                QtGui.QColor(100, 100, 100))
        else:
            self._brushes['local'] = QtGui.QBrush(QtCore.Qt.black)
            self._brushes['uploaded'] = QtGui.QBrush(QtCore.Qt.gray)

        self.widget.itemDoubleClicked.connect(self.open_file)
        self.parent.actionSelectAll.triggered.connect(self.select_all)
        self.parent.actionReverseSelection.triggered.connect(
            self.reverse_selection)

        self.widget.showEvent = self.showEvent
        self.widget.hideEvent = self.hideEvent

    def __del__(self):
        self._lock.acquire()

    @property
    def directory(self):
        """Current working dir.  """
        return self.parent.directory

    def showEvent(self, event):

        def _run():
            lock = self._lock
            while lock.acquire(False):
                try:
                    if self.widget.isVisible():
                        self.update()
                except RuntimeError:
                    pass
                time.sleep(1)
                lock.release()
        self.update()
        thread = threading.Thread(name='ListWidgetUpdate', target=_run)
        thread.daemon = True
        thread.start()
        event.accept()

    def hideEvent(self, event):
        event.accept()
        self._lock.acquire()
        self._lock.release()

    def update(self):
        """Update info.  """
        self.update_files()
        widget = self.widget
        local_files = self.local_files
        all_files = local_files + self.uploaded_files

        # Remove.
        for item in self.items():
            text = item.text()
            if text not in all_files:
                widget.takeItem(widget.indexFromItem(item).row())

            elif item.checkState() \
                    and isinstance(self.parent.get_dest(text, refresh=True), Exception):
                item.setCheckState(QtCore.Qt.Unchecked)

        for i in all_files:
            # Add.
            try:
                item = self.widget.findItems(
                    i, QtCore.Qt.MatchExactly)[0]
            except IndexError:
                item = QtWidgets.QListWidgetItem(i, widget)
                item.setCheckState(QtCore.Qt.Unchecked)
            # Set style.
            if i in local_files:
                item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                              QtCore.Qt.ItemIsEnabled)
                item.setForeground(self._brushes['local'])
            else:
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                item.setForeground(self._brushes['uploaded'])
                item.setCheckState(QtCore.Qt.Unchecked)

        widget.sortItems()

        # Count
        self.parent.labelCount.setText(
            '{}/{}/{}'.format(len(list(self.checked_files)), len(local_files), len(all_files)))

    def update_files(self):
        """Update local_files and uploaded_files.  """

        if not os.path.isdir(self.directory):
            return
        local_files = version_filter(i for i in os.listdir(self.directory)
                                     if i.endswith('.mov'))

        uploaded_files = []
        for i in list(local_files):
            src = os.path.join(self.directory, i)
            dst = self.parent.get_dest(i)
            if isinstance(dst, (str, unicode)) and is_same(src, dst):
                local_files.remove(i)
                uploaded_files.append(i)

        self.uploaded_files = uploaded_files
        self.local_files = local_files

    @property
    def checked_files(self):
        """Return files checked in listwidget.  """
        return (i.text() for i in self.items() if i.checkState())

    @property
    def is_use_burnin(self):
        """Use burn-in version when preview.  """
        return self.parent.checkBoxBurnIn.checkState()

    @QtCore.Slot(QtWidgets.QListWidgetItem)
    def open_file(self, item):
        """Open mov file for preview.  """

        filename = item.text()
        path = os.path.join(self.directory, filename)
        burn_in_path = os.path.join(
            self.directory, self.burnin_folder, filename)

        webbrowser.open(burn_in_path
                        if self.is_use_burnin and os.path.exists(burn_in_path)
                        else path)

    def items(self):
        """Item in list widget -> list."""

        widget = self.widget
        return list(widget.item(i) for i in xrange(widget.count()))

    def select_all(self):
        """Select all item in list widget.  """
        for item in self.items():
            if item.text() not in self.uploaded_files:
                item.setCheckState(QtCore.Qt.Checked)

    def reverse_selection(self):
        """Select all item in list widget.  """
        for item in self.items():
            if item.text() not in self.uploaded_files:
                if item.checkState():
                    item.setCheckState(QtCore.Qt.Unchecked)
                else:
                    item.setCheckState(QtCore.Qt.Checked)


def main():
    """Run this script standalone.  """

    app = QApplication(sys.argv)
    frame = Dialog()
    frame.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
