# -*- coding=UTF-8 -*-
"""Batch comp runner.  """
from __future__ import absolute_import

import os
import webbrowser
import logging
import traceback
import re
import time
from multiprocessing.dummy import Pool, Process, cpu_count
from subprocess import Popen, PIPE

import nuke
import nukescripts
import psutil

import wlf.config
from wlf.path import get_encoded, get_unicode
from wlf.notify import Progress, CancelledError
from wlf.decorators import run_async, run_in_main_thread

from comp import COMP_START_MESSAGE
from comp import Dialog as CompDialog
from comp import __file__ as script_file

__version__ = '0.2.3'

LOGGER = logging.getLogger('com.wlf.batchcomp')

# bitmask
IGNORE_EXISTED = 1 << 0
MULTI_THREADING = 1 << 1


class Config(wlf.config.Config):
    """BatchComp config.  """

    default = {
        'dir_pat': r'^.{4,}$',
        'output_dir': 'E:/precomp',
        'input_dir': 'Z:/SNJYW/Render/EP',
        'txt_name': '镜头备注',
        'exclude_existed': True,
    }
    path = os.path.expanduser(u'~/.nuke/wlf.batchcomp.json')


CONFIG = Config()


class Dialog(nukescripts.PythonPanel):
    """Dialog UI of class BatchComp."""

    knob_list = [
        (nuke.File_Knob, 'input_dir', '输入文件夹'),
        (nuke.File_Knob, 'output_dir', '输出文件夹'),
        (nuke.Boolean_Knob, 'exclude_existed', '排除已输出镜头'),
        (nuke.Script_Knob, 'setting', '合成设置'),
        (nuke.Text_Knob, '', ''),
        (nuke.String_Knob, 'txt_name', ''),
        (nuke.Script_Knob, 'generate_txt', '生成'),
        (nuke.Multiline_Eval_String_Knob, 'info', ''),
        (nuke.String_Knob, 'dir_pat', '文件夹正则'),
        (nuke.Script_Knob, 'reset', '重置'),
    ]

    def __init__(self):
        nukescripts.PythonPanel.__init__(self, '批量合成', 'com.wlf.batchcomp')
        self._shot_list = None

        for i in self.knob_list:
            k = i[0](*i[1:])
            try:
                k.setValue(CONFIG.get(i[1]))
            except TypeError:
                pass
            self.addKnob(k)
        for i in ('exclude_existed',):
            self.knobs()[i].setFlag(nuke.STARTLINE)
        self.knobs()['generate_txt'].setLabel(
            '生成 {}.txt'.format(self.txt_name))

    def __getattr__(self, name):
        return self.knobs()[name].value()

    def knobChanged(self, knob):
        """Overrride for buttons."""

        name = knob.name()

        if name == 'OK':
            self.batchcomp.start()
        elif name == 'reset':
            self.reset()
        elif name == 'generate_txt':
            self.generate_txt()
        elif name == 'setting':
            self.show_setting()
        elif name == 'txt_name':
            self.knobs()['generate_txt'].setLabel(
                '生成 {}.txt'.format(self.txt_name))
        elif name in self.knobs():
            CONFIG[name] = knob.value()

        self.update()

    @run_async
    @run_in_main_thread
    def show_setting(self):
        """Show comp setting.  """

        CompDialog().showModalDialog()

    def generate_txt(self):
        """Generate txt contain shot list.  """

        shots = self.batchcomp.get_shot_list()
        path = os.path.join(self.output_dir, '{}.txt'.format(self.txt_name))
        line_width = max(len(i) for i in shots)
        if os.path.exists(get_encoded(path)) and not nuke.ask('文件已存在, 是否覆盖?'):
            return
        with open(get_encoded(path), 'w') as f:
            f.write('\n\n'.join('{: <{width}s}: '.format(i, width=line_width)
                                for i in shots))
        webbrowser.open(get_unicode(path))

    @property
    def txt_name(self):
        """Output txt name. """
        return self.knobs()['txt_name'].value()

    @property
    def batchcomp(self):
        """Batch comp object related to current setting. """

        i_dir = self.input_dir
        o_dir = self.output_dir

        flags = 0
        if self.knobs()['exclude_existed'].value():
            flags |= IGNORE_EXISTED
        if psutil.virtual_memory().free > 16 * 1024 ** 3:
            flags |= MULTI_THREADING

        return BatchComp(i_dir, o_dir, flags=flags)

    def reset(self):
        """Reset re pattern.  """
        for i in ('dir_pat',):
            knob = self.knobs()[i]
            knob.setValue(CONFIG.default.get(i))
            self.knobChanged(knob)

    def update(self):
        """Update ui info and button enabled."""

        def _info():
            _info = u'测试'
            self._shot_list = list(self.batchcomp.get_shot_list())
            if self._shot_list:
                _info = u'# 共{}个镜头\n'.format(len(self._shot_list))
                _info += u'\n'.join(self._shot_list)
            else:
                _info = u'找不到镜头'
            self.knobs()['info'].setValue(_info)

        def _button_enabled():
            _knobs = [
                'output_dir',
                'exclude_existed',
                'info',
                'OK',
            ]

            _isdir = os.path.isdir(CONFIG['input_dir'])
            if _isdir:
                for k in ['exclude_existed', 'info']:
                    self.knobs()[k].setEnabled(True)
                if self._shot_list:
                    for k in _knobs:
                        self.knobs()[k].setEnabled(True)
                else:
                    for k in set(_knobs) - set(['exclude_existed']):
                        self.knobs()[k].setEnabled(False)
            else:
                for k in _knobs:
                    self.knobs()[k].setEnabled(False)

        _info()
        _button_enabled()


class BatchComp(Process):
    """Multiple comp.  """

    def __init__(self, input_dir, output_dir, flags=IGNORE_EXISTED | MULTI_THREADING):
        super(BatchComp, self).__init__()

        self.input_dir = input_dir
        self.output_dir = output_dir
        self.flags = flags
        self._all_shots = tuple()

    def run(self):
        """Start process all shots with a processbar."""

        shots = self.get_shot_list()
        task = Progress('批量合成', total=len(shots))
        thread_count = cpu_count() if self.flags & MULTI_THREADING else 1
        pool = Pool(thread_count)
        shots_info = dict.fromkeys(self._all_shots, '本次未处理')

        def _run(cmd, shot):
            def _check_cancel():
                if task.is_cancelled():
                    raise CancelledError

            def _cancel_handler(proc):
                assert isinstance(proc, Popen)
                try:
                    while True:
                        if task.is_cancelled():
                            proc.terminate()
                            break
                        elif proc.poll() is not None:
                            break
                except OSError:
                    pass

            while self.flags & MULTI_THREADING and psutil.virtual_memory().free < 8 * 1024 ** 3:
                time.sleep(1)
                task.set(message='等待8G空闲内存……')

            if not self.flags & MULTI_THREADING:
                task.step(shot)
            try:
                _check_cancel()

                LOGGER.info('%s:开始', shot)
                proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
                Process(target=_cancel_handler, args=(proc,)).start()
                stderr = proc.communicate()[1]

                _check_cancel()
                if COMP_START_MESSAGE in stderr:
                    stderr = stderr.partition(
                        COMP_START_MESSAGE)[2].strip()

                if stderr:
                    shots_info[shot] = stderr
                elif proc.returncode:
                    shots_info[shot] = 'Nuke非正常退出: {}'.format(proc.returncode)
                else:
                    shots_info[shot] = '正常完成'
                LOGGER.info('%s:结束', shot)
            except CancelledError:
                shots_info[shot] = '用户取消'
            except:
                shots_info[shot] = traceback.format_exc()
                LOGGER.error('Unexpected exception during comp', exc_info=True)
                raise
            finally:
                if self.flags & MULTI_THREADING:
                    task.step()

        task.set(0, '正在使用 {} 线程进行……'.format(thread_count))
        for shot in shots:
            shot = os.path.basename(shot)
            output = os.path.join(
                CONFIG['output_dir'], '{}_v0.nk'.format(shot))
            input_dir = shot if os.path.isdir(
                shot) else os.path.join(CONFIG['input_dir'], shot)
            _cmd = u'"{nuke}" -t -priority low {script} "{input_dir}" "{output}"'.format(
                nuke=nuke.EXE_PATH,
                script=os.path.normcase(script_file).rstrip(u'c'),
                input_dir=input_dir,
                output=output
            )

            pool.apply_async(_run, args=(_cmd, shot))
        pool.close()
        pool.join()

        self.generate_report(shots_info)

    @classmethod
    def generate_report(cls, shots_info):
        """Generate batchcomp report.  """

        infos = ''
        for shot in sorted(shots_info.keys()):
            infos += u'''\
    <tr>
        <td class="shot"><img src="images/{0}_v0.jpg" class="preview"></img><br>{0}</td>
        <td class="info">{1}</td>
    </tr>
'''.format(shot, shots_info[shot])
        with open(os.path.join(__file__, '../comp.head.html')) as f:
            head = f.read()
        html_page = head
        html_page += u'''
<body>
    <table id="mytable">
    <tr>
        <th>镜头</th>
        <th>信息</th>
    </tr>
    {}
    </table>
</body>
'''.format(infos)
        log_path = os.path.join(CONFIG['output_dir'], u'批量合成日志.html')
        with open(log_path, 'w') as f:
            f.write(html_page.encode('UTF-8'))
        webbrowser.open(log_path)
        webbrowser.open(CONFIG['output_dir'])

    def get_shot_list(self):
        """Return shot_list generator from a config dict."""

        _dir = self.input_dir
        _out_dir = self.output_dir
        if not os.path.isdir(_dir):
            return

        _ret = os.listdir(_dir)
        if isinstance(_ret[0], str):
            _ret = tuple(get_unicode(i) for i in _ret)
        self._all_shots = _ret
        if self.flags & IGNORE_EXISTED:
            _ret = (i for i in _ret
                    if not os.path.exists(os.path.join(_out_dir, u'{}_v0.nk'.format(i)))
                    and not os.path.exists(os.path.join(_out_dir, u'{}.nk'.format(i))))
        _ret = (i for i in _ret if (
            re.match(CONFIG['dir_pat'], i) and os.path.isdir(os.path.join(_dir, i))))

        if not _ret:
            _dir = _dir.rstrip('\\/')
            _dirname = os.path.basename(_dir)
            if re.match(CONFIG['dir_pat'], _dir):
                _ret = [_dir]
        return sorted(_ret)
