# -*- coding=UTF-8 -*-
"""Upload files to server.  """

import os
import sys

from wlf import cgtwq
from wlf.Qt import QtCore, QtWidgets, QtCompat, QtGui
from wlf.Qt.QtWidgets import QDialog, QApplication, QFileDialog
from wlf.files import version_filter, copy, remove_version,\
    is_same, get_unicode, get_server, url_open, split_version
from wlf.progress import Progress, CancelledError, HAS_NUKE
import wlf.config

__version__ = '0.6.2'


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
    is_check_account = True
    burnin_folder = 'burn-in'

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
            self.actionOpenDir.triggered.connect(self.open_dir)
            self.actionOpenServer.triggered.connect(self.open_server)
            self.actionSelectAll.triggered.connect(self.select_all)
            self.actionReverseSelection.triggered.connect(
                self.reverse_selection)

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

            self.dirEdit.editingFinished.connect(self.listWidget.clear)
            self.listWidget.itemDoubleClicked.connect(self.open_file)

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
            self.checkBoxSubmit: 'IS_SUBMIT',
            self.checkBoxBurnIn: 'IS_BURN_IN',
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
            self._brushes['local'] = QtGui.QBrush(QtGui.QColor(200, 200, 200))
            self._brushes['uploaded'] = QtGui.QBrush(
                QtGui.QColor(100, 100, 100))
        else:
            self._brushes['local'] = QtGui.QBrush(QtCore.Qt.black)
            self._brushes['uploaded'] = QtGui.QBrush(QtCore.Qt.gray)

        self._cgtw_dests = {}
        self._showed_error_message = []

    def _start_update(self):
        """Start a thread for update."""

        _timer = QtCore.QTimer(self)
        _timer.timeout.connect(self.update_ui)
        _timer.start(0)

    def update_ui(self):
        """Update dialog UI content.  """
        files = self.files()
        mode = self.mode()

        def _list_widget():
            widget = self.listWidget
            all_files = files + self._uploaded_files

            for i in xrange(widget.count()):
                item = widget.item(i)
                if not item:
                    continue

                if item.text() not in all_files:
                    widget.takeItem(widget.indexFromItem(item).row())

                elif not self.get_dest(item.text()):
                    item.setCheckState(QtCore.Qt.Unchecked)

            for i in all_files:
                try:
                    item = self.listWidget.findItems(
                        i, QtCore.Qt.MatchExactly)[0]
                except IndexError:
                    item = QtWidgets.QListWidgetItem(i, widget)
                    item.setCheckState(QtCore.Qt.Unchecked)
                if i in files:
                    item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                                  QtCore.Qt.ItemIsEnabled)
                    item.setForeground(self._brushes['local'])
                else:
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    item.setForeground(self._brushes['uploaded'])
                    item.setCheckState(QtCore.Qt.Unchecked)

            widget.sortItems()

        _list_widget()
        checked_files = self.checked_files()
        if mode == 0:
            self.syncButton.setEnabled(bool(os.path.exists(get_server(self.server))
                                            and os.path.isdir(os.path.dirname(self.dest))
                                            and checked_files))
            self.syncButton.setText(u'上传至: {}'.format(self.dest))
        elif mode == 1:
            self.syncButton.setText(u'上传至CGTeamWork')
            self.syncButton.setEnabled(bool(checked_files))

    def files(self):
        """Return files in folder as list.  """

        self._uploaded_files = []
        if not os.path.isdir(self.dir):
            return []
        ret = version_filter(i for i in os.listdir(self.dir)
                             if i.endswith('.mov'))

        for i in list(ret):
            src = os.path.join(self.dir, i)
            dst = self.get_dest(i)
            if is_same(src, dst):
                ret.remove(i)
                self._uploaded_files.append(i)

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
                if self.is_check_account:
                    try:
                        cgtwq.Shot(split_version(i)[0]).check_account()
                    except cgtwq.AccountError as ex:
                        self.error(u'{}\n已被分配给:\t{}\n当前用户:\t\t{}'.format(
                            i, ex.owner or '<未分配>', ex.current))
                        continue
                    except (cgtwq.IDError, cgtwq.LoginError):
                        self.error(u'{}: 不能上传'.format(i))
                src = os.path.join(self.dir, i)
                dst = self.get_dest(i)
                copy(src, dst)
                if self.is_submit:
                    cgtwq.Shot(split_version(i)[0]).submit(
                        [dst], note='自MOV上传工具提交')

        except CancelledError:
            pass

        self.activateWindow()

    @QtCore.Slot(QtWidgets.QListWidgetItem)
    def open_file(self, item):
        """Open mov file for preview.  """
        filename = item.text()
        path = os.path.join(self.dir, filename)
        burn_in_path = os.path.join(self.dir, self.burnin_folder, filename)

        url_open(burn_in_path
                 if self.is_use_burnin and os.path.exists(burn_in_path)
                 else path,
                 isfile=True)

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

    def get_dest(self, filename):
        """Get destination for @filename. """
        mode = self.mode()
        if mode == 0:
            return os.path.join(self.dest, remove_version(filename))
        elif mode == 1:
            try:
                ret = self._cgtw_dests.get(filename) or cgtwq.Shot(
                    split_version(filename)[0]).video_dest
                self._cgtw_dests[filename] = ret
                return ret
            except cgtwq.LoginError:
                self.error(u'需要登录CGTeamWork')
            except cgtwq.IDError:
                self.error(u'\n{}: CGTW上未找到对应镜头'.format(filename))
        else:
            raise ValueError('No such mode. {}'.format(mode))

    def error(self, message):
        """Show error.  """
        if message not in self._showed_error_message:
            self.textEdit.append(message)
            self._showed_error_message.append(message)

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

    @property
    def is_submit(self):
        """Submit when upload or not.  """
        return self.checkBoxSubmit.checkState()

    @property
    def is_use_burnin(self):
        """Use burn-in version when preview.  """
        return self.checkBoxBurnIn.checkState()

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

    def list_items(self):
        """Item in list widget -> list."""

        widget = self.listWidget
        return list(widget.item(i) for i in xrange(widget.count()))

    def select_all(self):
        """Select all item in list widget.  """
        for item in self.list_items():
            if item.text() not in self._uploaded_files:
                item.setCheckState(QtCore.Qt.Checked)

    def reverse_selection(self):
        """Select all item in list widget.  """
        for item in self.list_items():
            if item.text() not in self._uploaded_files:
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
