# -*- coding=UTF-8 -*-
"""Upload files to server.  """

import os
import sys
import re
import time
import json
from subprocess import call, Popen, PIPE


if __name__ == '__main__':
    __file__ = os.path.abspath(sys.argv[0])

try:
    LIB_PATH = os.path.join(
        getattr(sys, '_MEIPASS', os.path.abspath('{}/../../'.format(__file__))), 'lib')
    sys.path.append(LIB_PATH)

    from ui_uploader import Ui_Dialog
    from wlf.Qt import QtCore, QtWidgets
    from wlf.Qt.QtWidgets import QDialog, QApplication, QFileDialog
    from wlf.files import version_filter, copy, remove_version, get_encoded
    import wlf.config
except ImportError:
    raise

__version__ = '0.1.0'


class Config(wlf.config.Config):
    """A disk config can be manipulated like a dict."""

    default = {
        'DIR': 'N:/',
        'SERVER': r'\\192.168.1.7\z',
        'PROJECT': 'SNJYW',
        'FOLDER': 'Comp\\mov',
        'EPISODE': '',
        'SCENE': '',
    }
    path = os.path.expanduser('~/.wlf.uploader.json')


def is_same(src, dst):
    """Check if src is same with dst.  """

    if not os.path.isfile(dst):
        return False
    if os.path.getmtime(src) == os.path.getmtime(dst):
        return True

    return False


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


class Dialog(QDialog, Ui_Dialog):
    """Mian GUI dialog.  """
    # TODO:ProgressBar.

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

            for edit, key in self.edits_key.iteritems():
                if isinstance(edit, QtWidgets.QLineEdit):
                    edit.editingFinished.connect(
                        lambda e=edit, k=key: _set_config(k, e.text())
                    )
                    edit.textChanged.connect(self.update)
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
            for qt_edit, k in self.edits_key.iteritems():
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
        QDialog.__init__(self, parent)
        self.setupUi(self)

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
            if os.path.isdir(self.dest) and files:
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
        self.destEdit.setText(self.dest)

    def files(self):
        """Return files in folder as list.  """

        self._ignore = []
        if not os.path.isdir(self.dir):
            return []
        ret = version_filter(i for i in os.listdir(self.dir)
                             if i.endswith('.mov'))

        if os.path.isdir(self.dest):
            all_items = ret
            ret = []
            for i in all_items:
                _src = os.path.join(self.dir, i)
                _dst = os.path.join(
                    self.dest, remove_version(i))
                if not is_same(_src, _dst):
                    ret.append(i)
                else:
                    self._ignore.append(i)
        return ret

    def upload(self):
        """Upload videos to server.  """

        video_dest = unicode(self._config['video_dest'])

        if os.path.exists(os.path.dirname(video_dest)):
            if not os.path.exists(video_dest):
                os.mkdir(video_dest)
        else:
            print(u'**错误** 视频上传文件夹不存在, 将不会上传。')
            return False

        for i in self.video_list():
            src = os.path.join(self.dir, i)
            dst = os.path.join(video_dest, remove_version(i))
            copy(src, dst)

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
        return ret

    @property
    def dir(self):
        """Current working dir.  """
        return self.dirEdit.text()

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
            self.dirEdit.setText(_dir)
            self._config['DIR'] = _dir

    def autoset(self):
        """Auto set fields by dir.  """
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
            self._config['SERVER'] = dir_

    def open_dir(self):
        """Open config['DIR'] in explorer.  """

        url_open('file://{}'.format(self._config['DIR']))

    def open_server(self):
        """Open config['SERVER'] in explorer.  """

        url_open('file://{}'.format(self._config['SERVER']))

    def closeEvent(self, event):
        """Override Qdialog closeEvent().  """
        print(2)


def main():
    """Run this script standalone.  """

    call(u'CHCP 936 & TITLE scenetools.console & CLS', shell=True)
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
    try:
        main()
    except SingleInstanceException as ex:
        active_pid(Config()['PID'])
        print(u'激活已经打开的实例')
    except SystemExit as ex:
        sys.exit(ex)
