# -*- coding=UTF-8 -*-
"""Batch comp runner.  """
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import re
import time
import traceback
import webbrowser
from multiprocessing.dummy import Pool, Process, cpu_count
from subprocess import PIPE, Popen

import nuke
import nukescripts  # pylint: disable=import-error
import psutil
from jinja2 import Environment, PackageLoader

import __about__
import wlf.config
from comp.__main__ import __path__
from comp.config import (IGNORE_EXISTED, MULTI_THREADING, START_MESSAGE,
                         BatchCompConfig)
from nuketools import iutf8, utf8
from wlf.decorators import run_async, run_in_main_thread
from wlf.notify import CancelledError, Progress
from wlf.path import get_encoded as e
from wlf.path import get_unicode as u

LOGGER = logging.getLogger('com.wlf.batchcomp')


CONFIG = BatchCompConfig()


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
                proc = Popen(cmd,
                             #  shell=True,
                             stdout=PIPE,
                             stderr=PIPE)
                Process(target=_cancel_handler, args=(proc,)).start()
                stderr = u(proc.communicate()[1])
                LOGGER.error(stderr)

                _check_cancel()
                if START_MESSAGE in stderr:
                    stderr = stderr.partition(
                        START_MESSAGE)[2].strip()

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
            _cmd = u'"{nuke}" -t -priority low "{script}" "{input_dir}" "{output}"'.format(
                nuke=nuke.EXE_PATH,
                script=__path__,
                input_dir=input_dir,
                output=output
            )
            LOGGER.debug(_cmd)

            pool.apply_async(_run, args=(_cmd, shot))
        pool.close()
        pool.join()

        self.generate_report(shots_info)

    @classmethod
    def generate_report(cls, shots_info):
        """Generate batchcomp report.  """

        assert isinstance(shots_info, dict)
        env = Environment(loader=PackageLoader(__about__.__name__))
        template = env.get_template('batchcomp.html')
        data = template.render(shots_info=sorted(shots_info.items()))

        log_path = os.path.join(CONFIG['output_dir'], u'批量合成日志.html')
        with open(e(log_path), 'w') as f:
            f.write(data.encode('UTF-8'))
        webbrowser.open(log_path)
        webbrowser.open(CONFIG['output_dir'])

    def get_shot_list(self):
        """Return shot_list generator from a config dict."""

        _dir = self.input_dir
        _out_dir = self.output_dir
        if not os.path.isdir(_dir):
            return []

        _ret = os.listdir(_dir)
        if isinstance(_ret[0], str):
            _ret = tuple(u(i) for i in _ret)
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
