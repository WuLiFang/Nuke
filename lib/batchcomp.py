# -*- coding=UTF-8 -*-
"""Batch comp runner.  """

import os
import webbrowser
import logging
import json
import traceback
from multiprocessing.dummy import Pool, Process, cpu_count
from subprocess import Popen, PIPE

import nuke
import nukescripts

from wlf.path import get_encoded, escape_batch
from wlf.notify import Progress, CancelledError

from comp import CONFIG, Comp, COMP_START_MESSAGE
from comp import __file__ as script_file

__version__ = '0.1.0'

LOGGER = logging.getLogger('com.wlf.batchcomp')


class Dialog(nukescripts.PythonPanel):
    """Dialog UI of class Comp."""

    knob_list = [
        (nuke.Tab_Knob, 'general_setting', '常用设置'),
        (nuke.File_Knob, 'input_dir', '输入文件夹'),
        (nuke.File_Knob, 'output_dir', '输出文件夹'),
        (nuke.File_Knob, 'mp', '指定MP'),
        (nuke.File_Knob, 'mp_lut', 'MP LUT'),
        (nuke.Boolean_Knob, 'exclude_existed', '排除已输出镜头'),
        (nuke.Boolean_Knob, 'autograde', '自动亮度'),
        (nuke.Tab_Knob, 'filter', '正则过滤'),
        (nuke.String_Knob, 'footage_pat', '素材名'),
        (nuke.String_Knob, 'dir_pat', '路径'),
        (nuke.String_Knob, 'tag_pat', '标签'),
        (nuke.Script_Knob, 'reset', '重置'),
        (nuke.EndTabGroup_Knob, 'end_tab', ''),
        (nuke.String_Knob, 'txt_name', ''),
        (nuke.Script_Knob, 'generate_txt', '生成'),
        (nuke.Multiline_Eval_String_Knob, 'info', ''),
    ]

    def __init__(self):
        nukescripts.PythonPanel.__init__(self, '吾立方批量合成', 'com.wlf.multicomp')
        self._shot_list = None

        for i in self.knob_list:
            k = i[0](i[1], i[2])
            try:
                k.setValue(CONFIG.get(i[1]))
            except TypeError:
                pass
            self.addKnob(k)
        self.knobs()['exclude_existed'].setFlag(nuke.STARTLINE)
        self.knobs()['reset'].setFlag(nuke.STARTLINE)
        self.knobs()['generate_txt'].setLabel(
            '生成 {}.txt'.format(self.txt_name))

    def knobChanged(self, knob):
        """Overrride for buttons."""

        if knob is self.knobs()['OK']:
            BatchComp(self._shot_list).start()
        elif knob is self.knobs()['info']:
            self.update()
        elif knob is self.knobs()['reset']:
            self.reset()
        elif knob is self.knobs()['generate_txt']:
            self.generate_txt()
        elif knob is self.knobs()['txt_name']:
            self.knobs()['generate_txt'].setLabel(
                '生成 {}.txt'.format(self.txt_name))
        else:
            CONFIG[knob.name()] = knob.value()
            CONFIG[knob.name()] = knob.value()
            self.update()

    def generate_txt(self):
        """Generate txt contain shot list.  """
        path = os.path.join(self.output_dir, '{}.txt'.format(self.txt_name))
        line_width = max(len(i) for i in self.shot_list)
        if os.path.exists(get_encoded(path)) and not nuke.ask('文件已存在, 是否覆盖?'):
            return
        with open(get_encoded(path), 'w') as f:
            f.write('\n\n'.join('{: <{width}s}: '.format(i, width=line_width)
                                for i in self.shot_list))
        webbrowser.open(path)

    @property
    def txt_name(self):
        """Output txt name. """
        return self.knobs()['txt_name'].value()

    def reset(self):
        """Reset re pattern.  """
        for i in ('footage_pat', 'dir_pat', 'tag_pat'):
            knob = self.knobs()[i]
            knob.setValue(CONFIG.default.get(i))
            self.knobChanged(knob)

    @property
    def shot_list(self):
        """Shot name list. """
        return self._shot_list

    @property
    def output_dir(self):
        """Output directory. """
        return self.knobs()['output_dir'].value()

    def update(self):
        """Update ui info and button enabled."""

        def _info():
            _info = u'测试'
            self._shot_list = list(Comp.get_shot_list(CONFIG))
            if self._shot_list:
                _info = u'# 共{}个镜头\n'.format(len(self._shot_list))
                _info += u'\n'.join(self._shot_list)
            else:
                _info = u'找不到镜头'
            self.knobs()['info'].setValue(_info)

        def _button_enabled():
            _knobs = [
                'output_dir',
                'mp',
                'exclude_existed',
                'autograde',
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

    def __init__(self, shot_list):
        super(BatchComp, self).__init__()
        self._shot_list = list(shot_list)
        self.shot_info = dict.fromkeys(Comp.get_shot_list(
            CONFIG, include_existed=True), '本次未处理')

    def run(self):
        """Start process all shots with a processbar."""

        task = Progress('批量合成', total=len(self._shot_list))
        pool = Pool()
        shot_info = self.shot_info

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
                    shot_info[shot] = stderr
                elif proc.returncode:
                    shot_info[shot] = 'Nuke非正常退出: {}'.format(proc.returncode)
                else:
                    shot_info[shot] = '正常完成'
                LOGGER.info('%s:结束', shot)
            except CancelledError:
                shot_info[shot] = '用户取消'
            except:
                shot_info[shot] = traceback.format_exc()
                LOGGER.error('Unexpected exception during comp', exc_info=True)
                raise
            finally:
                task.step()

        task.set(0, '正在使用 {} 线程进行……'.format(cpu_count()))
        for shot in self._shot_list:
            CONFIG['shot'] = os.path.basename(shot)
            CONFIG['save_path'] = os.path.join(
                CONFIG['output_dir'], '{}_v0.nk'.format(CONFIG['shot']))
            CONFIG['footage_dir'] = shot if os.path.isdir(
                shot) else os.path.join(CONFIG['input_dir'], CONFIG['shot'])
            _cmd = u'"{nuke}" -t -priority low {script} "{CONFIG}"'.format(
                nuke=nuke.EXE_PATH,
                script_file=os.path.normcase(script_file).rstrip(u'c'),
                CONFIG=get_encoded(escape_batch(json.dumps(CONFIG)))
            )

            pool.apply_async(_run, args=(_cmd, shot))
        pool.close()
        pool.join()

        self.generate_report()

    def generate_report(self):
        """Generate batchcomp report.  """

        shot_info = self.shot_info

        infos = ''
        for shot in sorted(shot_info.keys()):
            infos += u'''\
    <tr>
        <td class="shot"><img src="images/{0}_v0.jpg" class="preview"></img><br>{0}</td>
        <td class="info">{1}</td>
    </tr>
'''.format(shot, shot_info[shot])
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
