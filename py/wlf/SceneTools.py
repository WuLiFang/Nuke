# -*- coding=UTF-8 -*-

import os, sys
import locale
import re
import time
import json

from subprocess import call, Popen, PIPE
from PySide import QtCore, QtGui
from PySide.QtGui import QDialog, QApplication, QFileDialog
from ui_scenetools_dialog import Ui_Dialog

VERSION = 0.52

SYS_CODEC = locale.getdefaultlocale()[1]
script_codec = 'UTF-8'

def pause():
    # call(u'PAUSE', shell=True)
    print(u'')
    for i in range(5)[::-1]:
        sys.stdout.write(u'\r{:2d}'.format(i+1))
        time.sleep(1)
    sys.stdout.write(u'\r          ')
    print(u'')

class Config(dict):
    default = {
        'SERVER': r'\\192.168.1.7\z', 
        'SIMAGE_FOLDER': r'Comp\image', 
        'SVIDEO_FOLDER': r'Comp\mov', 
        'NUKE': r'C:\Program Files\Nuke10.0v4\Nuke10.0.exe', 
        'DIR': 'N://', 
        'PROJECT': 'SNJYW', 
        'EP': '', 
        'SCENE': '', 
        'CSHEET_FFNAME': 'images', 
        'CSHEET_PREFIX': 'Contactsheet', 
        'VIDEO_FNAME': 'mov', 
        'IMAGE_FNAME': 'images', 
        'isImageUp': 2, 
        'isImageDown': 2, 
        'isVideoUp': 2, 
        'isVideoDown': 0, 
        'isCSheetUp': 0, 
        'isCSheetOpen': 2, 
        'csheet': '',
        'BACKDROP_DIR': '',
        'backdrop_name': '',
        'csheet_footagedir': '',
        'PID': '',
    }
    path = os.path.expanduser('~/.wlf.scenetools.json')
    psetting_bname = '.projectsettings.json'

    def __init__(self):
        self.update(dict(self.default))
        self.read()
        try:
            os.chdir(self['DIR'])
        except WindowsError as e:
            print(e)

    def __setitem__(self, key, value):
        print(key, value)
        if key == 'DIR':
            self.change_dir(value)
        dict.__setitem__(self, key, value)
        self.set_path()
        self.write()

    def write(self):
        with open(self.path, 'w') as f:
            json.dump(self, f, indent=4, sort_keys=True)
        try:
            with open(self.psetting_bname, 'w') as f:
                settings = [
                    'PROJECT',
                    'EP',
                    'SCENE',
                    'VIDEO_FNAME',
                    'IMAGE_FNAME',
                    'backdrop_name',
                    'csheet_footagedir',
                    'backdrop',
                    'csheet'
                ]
                psettings = {}
                for i in settings:
                    psettings[i] = self[i]
                json.dump(psettings, f, indent=4, sort_keys=True)
        except IOError:
            pass

    def read(self):
        if os.path.isfile(self.path):
            with open(self.path) as f:
                self.update(dict(json.load(f)))
        if os.path.isfile(self.psetting_bname):
            with open(self.psetting_bname) as f:
                self.update(dict(json.load(f)))

    def set_path(self):
        self.setConfigByDir()
        self.setSyncPath()
        self.setCSheetPath()
        self.setBackDropPath()

    def change_dir(self, dir):
        if os.path.isdir(dir) and dir != self['DIR']:
            os.chdir(dir)
            print(u'工作目录改为: {}'.format(os.getcwd()))
            self.read()

    def setSyncPath(self):
        dict.__setitem__(self, 'csheet_dest', os.path.join(self['SERVER'], self['PROJECT'], self['SIMAGE_FOLDER'], time.strftime('%m%d')))
        dict.__setitem__(self, 'image_dest', os.path.join(self['SERVER'], self['PROJECT'], self['SIMAGE_FOLDER'], self['EP'], self['SCENE']))
        dict.__setitem__(self, 'video_dest', os.path.join(self['SERVER'], self['PROJECT'], self['SVIDEO_FOLDER'], self['EP'], self['SCENE']))

    def setCSheetPath(self):
        _csheet_name = self['CSHEET_PREFIX']
        if self['EP'] and self['SCENE']:
            _csheet_name += '_{}_{}.jpg'.format(self['EP'], self['SCENE'])
        else:
            _csheet_name += '_{}.jpg'.format(time.strftime('%y%m%d_%H%M'))
        dict.__setitem__(self, 'csheet_name', _csheet_name)
        dict.__setitem__(self, 'csheet', os.path.join(self['DIR'], self['csheet_name']))
        dict.__setitem__(self, 'csheet_dest', os.path.join(self['SERVER'], self['PROJECT'], self['SIMAGE_FOLDER'], time.strftime('%m%d')))
        dict.__setitem__(self, 'csheet_footagedir', os.path.join(self['DIR'], self['CSHEET_FFNAME']))

    def setBackDropPath(self):
         dict.__setitem__(self, 'backdrop', os.path.join(self['BACKDROP_DIR'], self['backdrop_name']))
        
    def setConfigByDir(self):
        pat = re.compile(r'.*\\(ep.*?)\\.*\\(.+)', flags=re.I)
        match = pat.match(self['DIR'])
        if match:
             dict.__setitem__(self, 'EP', match.groups()[0])
             dict.__setitem__(self, 'SCENE', match.groups()[1])

def copy(src, dst):
    cmd = u'XCOPY /Y /V "{}" "{}"'.format(unicode(src), unicode(dst)).encode(SYS_CODEC)
    call(cmd)

class SingleInstanceException(Exception):
    def __str__(self):
        return u'已经有另一个实例在运行了'


class SingleInstance(object):
    def __init__(self):
        PID = Config()['PID']
        if isinstance(PID, int) and self.is_pid_exists(PID):
            raise SingleInstanceException
        Config()['PID'] = os.getpid()

    def is_pid_exists(self, pid):
        if sys.platform == 'win32':
            _proc = Popen('TASKLIST /FI "PID eq {}" /FO CSV /NH'.format(pid), stdout=PIPE)
            _stdout = _proc.communicate()[0]
            return '"{}"'.format(pid) in _stdout

class Sync(object):
    def __init__(self):
        self._config = Config()
        self._image_ignore = []
        self._video_ignore = []

    def image_list(self):
        self._image_ignore = []
        _dir = self._config['IMAGE_FNAME']
        if not os.path.isdir(_dir):
            return False
        _ret = list(i for i in os.listdir(_dir) if i.endswith('.jpg'))
        
        if os.path.isdir(self._config['image_dest']):
            _all_items = _ret
            _ret = []
            for i in _all_items:
                _src = os.path.join(self._config['IMAGE_FNAME'], i)
                _dst = os.path.join(self._config['image_dest'], i)
                if os.path.isfile(_dst) and os.path.getmtime(_src) == os.path.getmtime(_dst):
                    self._image_ignore.append(i)
                else:
                    _ret.append(i)
        return _ret

    def video_list(self):
        self._video_ignore = []
        _dir = self._config['VIDEO_FNAME']
        if not os.path.isdir(_dir):
            return False
        _ret = list(i for i in os.listdir(_dir) if i.endswith('.mov'))

        if os.path.isdir(self._config['video_dest']):
            _all_items = _ret
            _ret = []
            for i in _all_items:
                _src = os.path.join(self._config['VIDEO_FNAME'], i)
                _dst = os.path.join(self._config['video_dest'], i)
                if os.path.isfile(_dst) and os.path.getmtime(_src) == os.path.getmtime(_dst):
                    self._video_ignore.append(i)
                else:
                    _ret.append(i)
        return _ret

    def ignore_list(self):
        _ret = []
        if self._config['isVideoUp']:
            _ret += self._image_ignore
        if self._config['isImageUp']:
            _ret += self._video_ignore
        return _ret
    
    def uploadVideos(self):
        video_dest = unicode(self._config['video_dest'])

        if os.path.exists(os.path.dirname(video_dest)):
            if not os.path.exists(video_dest):
                os.mkdir(video_dest)
        else:
            print(u'**错误** 视频上传文件夹不存在, 将不会上传。')
            return False

        for i in self.video_list():
            src = os.path.join(self._config['VIDEO_FNAME'], i)
            dst = video_dest
            copy(src, dst)

    def downloadVideos():
        pass

    def uploadImages(self):
        dest = unicode(self._config['image_dest'])
        print(dest)
        if os.path.isdir(os.path.dirname(dest)):
            if not os.path.isdir(dest):
                os.mkdir(dest)
        else:
            print(u'**错误** 图片上传文件夹不存在, 将不会上传。')
            return False

        for i in self.image_list():
            src = os.path.join(self._config['IMAGE_FNAME'], i)
            dst = dest
            copy(src, dst)

    def downloadImages(self):
        src = self._config['image_dest']
        dst = self._config['IMAGE_FNAME']
        print(u'## 下载单帧: {} -> {}'.format(src, dst))
        call('XCOPY /Y /D /I /V "{}\\*.jpg" "{}"'.format(src, dst))

    def uploadCSheet(self):
        dest = self._config['csheet_dest']

        if os.path.isdir(os.path.dirname(dest)):
            if not os.path.isdir(dest):
                os.mkdir(dest)
        else:
            return False
            print(u'**错误** 色板上传文件夹不存在, 将不会上传。')

        copy(self._config['csheet'], dest)

class Dialog(QDialog, Ui_Dialog, SingleInstance):

    def __init__(self, parent=None):
        SingleInstance.__init__(self)
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.version_label.setText('v{}'.format(VERSION))

        self.edits_key = {
            self.serverEdit: 'SERVER', 
            self.videoFolderEdit: 'SVIDEO_FOLDER', 
            self.imageFolderEdit: 'SIMAGE_FOLDER', 
            self.nukeEdit: 'NUKE', 
            self.dirEdit: 'DIR', 
            self.projectEdit: 'PROJECT', 
            self.epEdit: 'EP', 
            self.scEdit: 'SCENE', 
            self.csheetFFNameEdit: 'CSHEET_FFNAME', 
            self.csheetPrefixEdit: 'CSHEET_PREFIX', 
            self.imageFNameEdit: 'IMAGE_FNAME', 
            self.videoFNameEdit: 'VIDEO_FNAME', 
            self.videoDestEdit: 'video_dest', 
            self.imageDestEdit: 'image_dest', 
            self.csheetNameEdit: 'csheet_name', 
            self.csheetDestEdit: 'csheet_dest',
            self.imageUpCheck: 'isImageUp', 
            self.imageDownCheck: 'isImageDown', 
            self.videoUpCheck: 'isVideoUp', 
            self.videoDownCheck: 'isVideoDown', 
            self.csheetUpCheck: 'isCSheetUp', 
            self.csheetOpenCheck: 'isCSheetOpen',
            self.backDropBox: 'backdrop_name'
        }
        self._config = Config()
        self._sync = Sync()
        _icon = self.style().standardIcon(QtGui.QStyle.SP_FileDialogListView)
        self.setWindowIcon(_icon)
        _icon = self.style().standardIcon(QtGui.QStyle.SP_DirOpenIcon)
        self.toolButtonOpenDir.setIcon(_icon)
        self.toolButtonOpenServer.setIcon(_icon)
        _icon = self.style().standardIcon(QtGui.QStyle.SP_DialogOpenButton)
        self.dirButton.setIcon(_icon)
        self.serverButton.setIcon(_icon)
        self.nukeButton.setIcon(_icon)
        _icon = self.style().standardIcon(QtGui.QStyle.SP_MediaPlay)
        self.sheetButton.setIcon(_icon)
        _icon = self.style().standardIcon(QtGui.QStyle.SP_FileIcon)
        self.openButton.setIcon(_icon)
        _icon = self.style().standardIcon(QtGui.QStyle.SP_FileDialogToParent)
        self.syncButton.setIcon(_icon)
        _icon = self.style().standardIcon(QtGui.QStyle.SP_FileDialogListView)
        self.toolBox.setItemIcon(0, _icon)
        _icon = self.style().standardIcon(QtGui.QStyle.SP_ComputerIcon)
        self.toolBox.setItemIcon(1, _icon)

        self.initBackdrop()
        self.update()

        self.connect_actions()
        self.connectEdits()

    def connect_actions(self):
        self.actionSheet.triggered.connect(self.create_sheet)
        self.actionDir.triggered.connect(self.ask_dir)
        self.actionNuke.triggered.connect(self.ask_nuke)
        self.actionOpen.triggered.connect(self.open_sheet)
        self.actionSync.triggered.connect(self.sync)
        self.actionServer.triggered.connect(self.ask_server)
        self.actionUpdateUI.triggered.connect(self.update)
        self.actionOpenDir.triggered.connect(self.open_dir)
        self.actionOpenServer.triggered.connect(self.open_server)

    def connectEdits(self):
        for edit, key in self.edits_key.iteritems():
            if isinstance(edit, QtGui.QLineEdit):
                edit.textChanged.connect(lambda text, k=key: self._config.__setitem__(k, text))
                edit.textChanged.connect(self.update)
            elif isinstance(edit, QtGui.QCheckBox):
                edit.stateChanged.connect(lambda state, k=key: self._config.__setitem__(k, state))
                edit.stateChanged.connect(self.update)
            elif isinstance(edit, QtGui.QComboBox):
                edit.currentIndexChanged.connect(lambda index, e=edit, k=key: self._config.__setitem__(k, e.itemText(index)))
            else:
                print(u'待处理的控件: {} {}'.format(type(edit), edit))

    def create_sheet(self):
        self.hide()
        active_pid(self._config['PID'])
        cfg = self._config
        if __name__ == '__main__':
            script = os.path.join(unicode(sys.argv[0], SYS_CODEC), '../csheet.py')
        else:
            script = os.path.join(__file__, '../csheet.py')
        _json = os.path.join(cfg['DIR'], Config.psetting_bname)
        _cmd = u'"{NUKE}" -t "{script}" "{json}"'.format(NUKE=cfg['NUKE'], script=script, json=_json)
        print(_cmd)
        call(_cmd.encode(SYS_CODEC))
        if self._config['isCSheetOpen']:
            self.open_sheet()
        if self._config['isCSheetUp']:
            self._sync.uploadCSheet()
        self.show()

    def open_sheet(self):
        if os.path.exists(self._config['csheet']):
            url_open('file://' + self._config['csheet'])

    def update(self):
        def _edits():
            for q, k in self.edits_key.iteritems():
                try:
                    if isinstance(q, QtGui.QLineEdit):
                        q.setText(self._config[k])
                    elif isinstance(q, QtGui.QCheckBox):
                        q.setCheckState(QtCore.Qt.CheckState(self._config[k]))
                    elif isinstance(q, QtGui.QComboBox):
                        q.setCurrentIndex(q.findText(self._config[k]))
                except KeyError as e:
                    print(e)

        def _button_enabled():
            dir = self._config['DIR']
            if os.path.isdir(dir):
                self.sheetButton.setEnabled(True)
                self.syncButton.setEnabled(True)
            else:
                self.sheetButton.setEnabled(False)
                self.syncButton.setEnabled(False)

            if os.path.isfile(self._config['csheet']):
                self.openButton.setEnabled(True)
            else:
                self.openButton.setEnabled(False)

        def _list_widget():
            _list = self.listWidget
            _page_index = self.toolBox.currentIndex()
            print('_page_index', _page_index)
            _list.clear()
            if _page_index == 1:
                _all_items = []
                _info = []
                if self._config['isImageUp']:
                    _image_list = self._sync.image_list()
                    if isinstance(_image_list, list):
                        _all_items += _image_list
                    else:
                        _info += [u'#图像文件夹不存在']
                if self._config['isVideoUp']:
                    _video_list = self._sync.video_list()
                    if isinstance(_video_list, list):
                        _all_items += _video_list
                    else:
                        _info += [u'#视频文件夹不存在']
                map(_list.addItem, _info)
                map(lambda x: _list.addItem(u'将上传: {}'.format(x)), _all_items)
                for i in self._sync.ignore_list():
                    _list.addItem(u'无需上传: {}'.format(i))
            elif _page_index == 2:
                pass
        print('upadeted')
        _edits()
        _button_enabled()
        _list_widget()

    def ask_dir(self):
        _fileDialog = QFileDialog()
        _dir = _fileDialog.getExistingDirectory(dir=os.path.dirname(self._config['DIR']))
        if _dir:
            self._config['DIR'] = _dir
            self.update()

    def ask_nuke(self):
        _fileDialog = QFileDialog()
        _fileNames, _selectedFilter = _fileDialog.getOpenFileName(dir=os.getenv('ProgramFiles'), filter='*.exe')
        if _fileNames:
            self._config['NUKE'] = _fileNames
            self.update()

            
    def initBackdrop(self):
        self._config['BACKDROP_DIR'] = unicode(os.path.join(os.path.dirname(unicode(sys.argv[0], SYS_CODEC)), u'Backdrops'))
        dir = self._config['BACKDROP_DIR']
        box = self.backDropBox
        if not os.path.exists(dir):
            os.mkdir(dir)
        bd_list = os.listdir(dir)
        for item in bd_list:
            box.addItem(item)
        self._config['backdrop_name'] = box.currentText()
        box.addItem(u'纯黑')
        
    def ask_server(self):
        fileDialog = QFileDialog()
        dir = fileDialog.getExistingDirectory(dir=os.path.dirname(self._config['SERVER']))
        if dir:
            self._config['SERVER'] = dir
            self.update()
      
    def sync(self):
        cfg = self._config
        if cfg['isImageDown']:
            self._sync.downloadImages()
        if cfg['isImageUp']:
            self._sync.uploadImages()
        if cfg['isVideoUp']:
            self._sync.uploadVideos()
        self.update()

    def open_dir(self):
        url_open('file://{}'.format(self._config['DIR']))

    def open_server(self):
        url_open('file://{}'.format(self._config['SERVER']))

def main():
    call(u'CHCP 936 & TITLE scenetools.console & CLS', shell=True)
    app = QApplication(sys.argv)
    frame = Dialog()
    frame.show()
    sys.exit(app.exec_())

def call_from_nuke():
    frame = Dialog()
    frame.show()

def active_pid(pid):
    if __name__ == '__main__':
        _file = sys.argv[0]
    else:
        _file = __file__
    _cmd = '"{}" "{}"'.format(os.path.abspath(os.path.join(_file, '../active_pid.exe')), pid)
    Popen(_cmd)

def url_open(url):
    _cmd = "rundll32.exe url.dll,FileProtocolHandler {}".format(url)
    Popen(_cmd)

if __name__ == '__main__':
    try:
        main()
    except SingleInstanceException as e:
        active_pid(Config()['PID'])
        print(u'激活已经打开的实例')
    except SystemExit as e:
        sys.exit(e)
    except:
        import traceback
        traceback.print_exc()
        pause()