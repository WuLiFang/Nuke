# -*- coding=UTF-8 -*-
"""Upload files to server.  """

import os
import sys
import re
from subprocess import Popen, PIPE

from wlf.Qt import QtCore, QtWidgets, QtCompat
from wlf.Qt.QtWidgets import QDialog, QApplication, QFileDialog
from wlf.files import version_filter, copy, remove_version, is_same, get_unicode, get_server
from wlf.progress import Progress, CancelledError, HAS_NUKE
import wlf.config

__version__ = '0.4.3'


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


class SingleInstanceException(Exception):
    """Indicate not single instance.  """

    def __str__(self):
        return u'已经有另一个实例在运行了'


def check_single_instance():
    """Raise SingleInstanceException if not run in singleinstance."""

    pid = Config()['PID']
    if isinstance(pid, int) and is_pid_exists(pid):
        raise SingleInstanceException
    Config()['PID'] = os.getpid()


def is_pid_exists(pid):
    """Check if pid existed.(Windows only)"""

    if sys.platform != 'win32':
        raise RuntimeError('Only support windows platfomr.')
    _proc = Popen(
        'TASKLIST /FI "PID eq {}" /FO CSV /NH'.format(pid),
        stdout=PIPE
    )
    _stdout = _proc.communicate()[0]
    ret = '"python.exe"' in _stdout \
        or '"scenetools.exe"' in _stdout \
        and '"{}"'.format(pid) in _stdout
    return ret


class Dialog(QDialog):
    """Mian GUI dialog.  """

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
            self.actionUpdateUI.triggered.connect(self.update)
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
                    edit.editingFinished.connect(self.update)
                elif isinstance(edit, QtWidgets.QCheckBox):
                    edit.stateChanged.connect(
                        lambda state, k=key: _set_config(k, state)
                    )
                    edit.stateChanged.connect(self.update)
                elif isinstance(edit, QtWidgets.QComboBox):
                    edit.currentIndexChanged.connect(
                        lambda index, ex=edit, k=key: _set_config(
                            k,
                            ex.itemText(index)
                        )
                    )
                else:
                    print(u'待处理的控件: {} {}'.format(type(edit), edit))

            self.dirEdit.editingFinished.connect(self.autoset)
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
        }
        self._config = Config()
        self.version_label.setText('v{}'.format(__version__))
        self._start_update()

        _icon()
        _actions()
        _edits()

    def _start_update(self):
        """Start a thread for update."""

        self.update()
        _timer = QtCore.QTimer(self)
        _timer.timeout.connect(self.update)
        _timer.start(1000)

    def update(self):
        """Update dialog UI content.  """
        files = self.files()

        def _button_enabled():
            if os.path.exists(get_server(self.server))\
                    and os.path.isdir(os.path.dirname(self.dest)) and files:
                self.syncButton.setEnabled(True)
            else:
                self.syncButton.setEnabled(False)

        def _list_widget():
            self.listWidget.clear()
            map(self.listWidget.addItem, files)
            if self._ignore:
                self.listWidget.addItem(u'# 无需上传')
                map(self.listWidget.addItem, self._ignore)

        _button_enabled()
        _list_widget()
        self.syncButton.setText(u'上传至: {}'.format(self.dest))

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

    def upload(self):
        """Upload videos to server.  """

        if not os.path.exists(self.dest):
            os.mkdir(self.dest)
        try:
            task = Progress()
            files = self.files()
            all_num = len(files)
            for index, i in enumerate(files):
                task.set(index * 100 // all_num, i)
                src = os.path.join(self.dir, i)
                dst = os.path.join(self.dest, remove_version(i))
                copy(src, dst)
        except CancelledError:
            self.activateWindow()
            return False
        self.close()

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


def call_from_nuke():
    """Run this script standaloe.  """

    frame = Dialog()
    frame.show()


def active_pid(pid):
    """Active window of given pid.  """

    if __name__ == '__main__':
        _file = sys.argv[0]
    else:
        _file = __file__
    _cmd = '"{}" "{}"'.format(
        os.path.abspath(os.path.join(_file, '../active_pid.exe')),
        pid
    )
    return Popen(_cmd)


def url_open(url):
    """Open url in explorer. """
    _cmd = "rundll32.exe url.dll,FileProtocolHandler {}".format(url)
    Popen(_cmd)


if __name__ == '__main__':
    main()
